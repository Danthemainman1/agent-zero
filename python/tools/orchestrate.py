"""
Orchestration tool for multi-agent parallel task execution.
"""

from python.helpers.tool import Tool, Response
from python.helpers.orchestrator import Orchestrator
import json


class OrchestrateTool(Tool):
    """
    Invokes multi-agent orchestration for complex tasks.
    Automatically decomposes task, executes in parallel, and verifies results.
    """

    async def execute(self, task: str = "", mode: str = "auto", **kwargs) -> Response:
        """
        Execute complex task using multi-agent orchestration.
        
        Args:
            task: The complex task to execute
            mode: Execution mode
                - "auto": Automatically choose best strategy (default)
                - "parallel": Force parallel execution
                - "sequential": Force sequential execution
                - "plan_only": Only create plan, don't execute
        """
        if not task:
            return Response(
                message="Error: No task provided. Please specify a task to orchestrate.",
                break_loop=False
            )

        # Create orchestrator
        orchestrator = Orchestrator(self.agent)

        # Log start
        self.agent.context.log.log(
            type="util",
            heading="icon://hub Starting Multi-Agent Orchestration",
            content=f"Task: {task[:100]}...\nMode: {mode}"
        )

        # Execute orchestration
        result = await orchestrator.execute(task, mode)

        # Format response
        if result.success:
            response_text = f"""## Orchestration Complete ✅

**Goal:** {result.main_goal}

**Execution Time:** {result.execution_time:.2f} seconds

### Results:
{json.dumps(result.results, indent=2, default=str)}

### Verification:
{json.dumps(result.verification, indent=2, default=str)}
"""
        else:
            response_text = f"""## Orchestration Failed ❌

**Goal:** {result.main_goal}

**Errors:**
{chr(10).join('- ' + e for e in result.errors)}

### Partial Results:
{json.dumps(result.results, indent=2, default=str) if result.results else 'None'}
"""

        return Response(message=response_text, break_loop=False)

    def get_log_object(self):
        return self.agent.context.log.log(
            type="tool",
            heading=f"icon://hub {self.agent.agent_name}: Multi-Agent Orchestration",
            content="",
            kvps=self.args
        )
