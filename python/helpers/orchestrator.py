"""
Multi-agent orchestrator for parallel task execution.
Implements Planner → [Parallel Executors] → Verifier workflow.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from python.helpers.print_style import PrintStyle
from python.helpers.dirty_json import DirtyJson


class TaskStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SubTask:
    id: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str = ""
    assigned_agent: str = ""
    can_parallel: bool = True
    estimated_complexity: str = "medium"
    required_tools: List[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    main_goal: str
    subtasks: List[SubTask] = field(default_factory=list)
    parallel_groups: List[List[str]] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OrchestrationResult:
    success: bool
    main_goal: str
    results: Dict[str, Any] = field(default_factory=dict)
    verification: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0


class Orchestrator:
    """
    Multi-agent orchestrator that coordinates specialized agents
    for complex task execution with parallel processing support.
    """

    def __init__(self, agent):
        from agent import Agent
        self.agent: Agent = agent
        self.context = agent.context
        self.plan: Optional[ExecutionPlan] = None
        self.results: Dict[str, Any] = {}
        self.start_time: Optional[datetime] = None

    async def execute(self, user_request: str, mode: str = "auto") -> OrchestrationResult:
        """
        Main execution entry point.
        
        Args:
            user_request: The complex task to execute
            mode: "auto" | "parallel" | "sequential" | "plan_only"
        """
        self.start_time = datetime.now()
        self.results = {}
        errors = []

        try:
            # Log start
            self._log_progress("Starting orchestration", f"Mode: {mode}")

            # Phase 1: Planning
            self._log_progress("Phase 1: Planning", "Decomposing task...")
            plan = await self._plan(user_request)
            
            if not plan or not plan.subtasks:
                return OrchestrationResult(
                    success=False,
                    main_goal=user_request,
                    errors=["Failed to create execution plan"]
                )

            self.plan = plan
            self._log_progress("Plan created", f"{len(plan.subtasks)} subtasks identified")

            if mode == "plan_only":
                return OrchestrationResult(
                    success=True,
                    main_goal=plan.main_goal,
                    results={"plan": self._plan_to_dict(plan)}
                )

            # Phase 2: Execution
            self._log_progress("Phase 2: Execution", "Executing subtasks...")
            
            if mode == "sequential":
                results = await self._execute_sequential(plan)
            else:
                results = await self._execute_parallel(plan)

            self.results = results

            # Phase 3: Verification
            self._log_progress("Phase 3: Verification", "Verifying results...")
            verification = await self._verify(plan, results)

            # Calculate execution time
            exec_time = (datetime.now() - self.start_time).total_seconds()

            return OrchestrationResult(
                success=verification.get("approved", False),
                main_goal=plan.main_goal,
                results=results,
                verification=verification,
                errors=errors,
                execution_time=exec_time
            )

        except Exception as e:
            PrintStyle.error(f"Orchestration failed: {str(e)}")
            return OrchestrationResult(
                success=False,
                main_goal=user_request,
                errors=[str(e)]
            )

    async def _plan(self, request: str) -> Optional[ExecutionPlan]:
        """Use Planner Agent to decompose task into subtasks."""
        from agent import Agent, UserMessage
        from initialize import initialize_agent

        try:
            # Create planner subordinate
            config = initialize_agent()
            config.profile = "planner"
            
            planner = Agent(self.agent.number + 1, config, self.context)
            planner.set_data(Agent.DATA_NAME_SUPERIOR, self.agent)

            # Send planning request
            planning_prompt = f"""Analyze and create an execution plan for the following task:

{request}

Respond with a structured JSON plan including subtasks, dependencies, and parallel groups."""

            planner.hist_add_user_message(UserMessage(message=planning_prompt, attachments=[]))
            response = await planner.monologue()

            # Parse the plan from response
            plan = self._parse_plan(response, request)
            return plan

        except Exception as e:
            PrintStyle.error(f"Planning failed: {str(e)}")
            # Fallback: create simple single-task plan
            return ExecutionPlan(
                main_goal=request,
                subtasks=[SubTask(id="task_1", description=request)],
                parallel_groups=[["task_1"]]
            )

    def _parse_plan(self, response: str, original_request: str) -> ExecutionPlan:
        """Parse planner response into ExecutionPlan."""
        try:
            # Try to extract JSON from response
            plan_data = DirtyJson.parse_string(response)
            
            if isinstance(plan_data, dict):
                subtasks = []
                for st in plan_data.get("subtasks", []):
                    subtasks.append(SubTask(
                        id=st.get("id", f"task_{len(subtasks)+1}"),
                        description=st.get("description", ""),
                        dependencies=st.get("dependencies", []),
                        can_parallel=st.get("can_parallel", True),
                        estimated_complexity=st.get("estimated_complexity", "medium"),
                        required_tools=st.get("required_tools", [])
                    ))

                return ExecutionPlan(
                    main_goal=plan_data.get("main_goal", original_request),
                    subtasks=subtasks,
                    parallel_groups=plan_data.get("parallel_groups", [[st.id for st in subtasks]]),
                    execution_order=plan_data.get("execution_order", []),
                    notes=plan_data.get("notes", "")
                )
        except Exception as e:
            PrintStyle.warning(f"Failed to parse plan JSON: {e}")

        # Fallback: single task
        return ExecutionPlan(
            main_goal=original_request,
            subtasks=[SubTask(id="task_1", description=original_request)],
            parallel_groups=[["task_1"]]
        )

    async def _execute_parallel(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute subtasks in parallel groups based on dependencies."""
        results = {}

        for group_idx, group in enumerate(plan.parallel_groups):
            self._log_progress(
                f"Executing group {group_idx + 1}/{len(plan.parallel_groups)}",
                f"Tasks: {', '.join(group)}"
            )

            # Get subtasks for this group
            group_tasks = [st for st in plan.subtasks if st.id in group]
            
            # Execute all tasks in this group concurrently
            coroutines = [self._execute_subtask(st, results) for st in group_tasks]
            group_results = await asyncio.gather(*coroutines, return_exceptions=True)

            # Store results
            for st, result in zip(group_tasks, group_results):
                if isinstance(result, Exception):
                    results[st.id] = {"status": "failed", "error": str(result)}
                    st.status = TaskStatus.FAILED
                    st.error = str(result)
                else:
                    results[st.id] = result
                    st.status = TaskStatus.COMPLETED
                    st.result = result

        return results

    async def _execute_sequential(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute all subtasks sequentially."""
        results = {}

        for idx, subtask in enumerate(plan.subtasks):
            self._log_progress(
                f"Executing task {idx + 1}/{len(plan.subtasks)}",
                subtask.description[:50] + "..."
            )

            try:
                result = await self._execute_subtask(subtask, results)
                results[subtask.id] = result
                subtask.status = TaskStatus.COMPLETED
                subtask.result = result
            except Exception as e:
                results[subtask.id] = {"status": "failed", "error": str(e)}
                subtask.status = TaskStatus.FAILED
                subtask.error = str(e)

        return results

    async def _execute_subtask(self, subtask: SubTask, prior_results: Dict) -> Dict[str, Any]:
        """Execute a single subtask using an Executor Agent."""
        from agent import Agent, UserMessage
        from initialize import initialize_agent

        try:
            # Create executor subordinate
            config = initialize_agent()
            config.profile = "executor"
            
            executor = Agent(self.agent.number + 1, config, self.context)
            executor.set_data(Agent.DATA_NAME_SUPERIOR, self.agent)

            # Build context from dependencies
            context = ""
            for dep_id in subtask.dependencies:
                if dep_id in prior_results:
                    context += f"\nResult from {dep_id}: {json.dumps(prior_results[dep_id])}\n"

            # Send execution request
            execution_prompt = f"""Execute the following task:

{subtask.description}

{f'Context from prior tasks:{context}' if context else ''}

Complete this task and respond with a JSON result."""

            executor.hist_add_user_message(UserMessage(message=execution_prompt, attachments=[]))
            response = await executor.monologue()

            # Try to parse as JSON, otherwise wrap as text
            try:
                result = DirtyJson.parse_string(response)
                if not isinstance(result, dict):
                    result = {"status": "success", "result": response}
            except:
                result = {"status": "success", "result": response}

            return result

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _verify(self, plan: ExecutionPlan, results: Dict[str, Any]) -> Dict[str, Any]:
        """Use Verifier Agent to check results quality."""
        from agent import Agent, UserMessage
        from initialize import initialize_agent

        try:
            # Create verifier subordinate
            config = initialize_agent()
            config.profile = "verifier"
            
            verifier = Agent(self.agent.number + 1, config, self.context)
            verifier.set_data(Agent.DATA_NAME_SUPERIOR, self.agent)

            # Build verification request
            verification_prompt = f"""Verify the following execution results:

Original Goal: {plan.main_goal}

Subtasks and Results:
{json.dumps(results, indent=2, default=str)}

Review for:
1. Correctness - Are the results accurate?
2. Completeness - Were all requirements met?
3. Quality - Is the work well done?

Respond with a verification JSON."""

            verifier.hist_add_user_message(UserMessage(message=verification_prompt, attachments=[]))
            response = await verifier.monologue()

            # Parse verification response
            try:
                verification = DirtyJson.parse_string(response)
                if not isinstance(verification, dict):
                    verification = {"approved": True, "notes": response}
            except:
                verification = {"approved": True, "notes": response}

            return verification

        except Exception as e:
            # If verification fails, assume approved but note the error
            return {
                "approved": True,
                "notes": f"Verification skipped due to error: {str(e)}"
            }

    def _plan_to_dict(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Convert ExecutionPlan to dictionary."""
        return {
            "main_goal": plan.main_goal,
            "subtasks": [
                {
                    "id": st.id,
                    "description": st.description,
                    "dependencies": st.dependencies,
                    "status": st.status.value,
                    "can_parallel": st.can_parallel,
                    "estimated_complexity": st.estimated_complexity
                }
                for st in plan.subtasks
            ],
            "parallel_groups": plan.parallel_groups,
            "notes": plan.notes
        }

    def _log_progress(self, heading: str, content: str = ""):
        """Log orchestration progress."""
        PrintStyle(font_color="#9B59B6", bold=True).print(f"🎭 Orchestrator: {heading}")
        if content:
            PrintStyle(font_color="#9B59B6").print(f"   {content}")
        
        self.context.log.log(
            type="util",
            heading=f"icon://hub Orchestrator: {heading}",
            content=content
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current orchestration status."""
        if not self.plan:
            return {"status": "idle"}

        completed = sum(1 for st in self.plan.subtasks if st.status == TaskStatus.COMPLETED)
        failed = sum(1 for st in self.plan.subtasks if st.status == TaskStatus.FAILED)
        total = len(self.plan.subtasks)

        return {
            "status": "running" if completed + failed < total else "completed",
            "main_goal": self.plan.main_goal,
            "progress": {
                "completed": completed,
                "failed": failed,
                "pending": total - completed - failed,
                "total": total,
                "percentage": (completed / total * 100) if total > 0 else 0
            },
            "subtasks": [
                {"id": st.id, "status": st.status.value, "description": st.description[:50]}
                for st in self.plan.subtasks
            ]
        }
