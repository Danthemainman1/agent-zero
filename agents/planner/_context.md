# Planner Agent

The Planner Agent is a specialized subordinate agent focused on task decomposition and execution planning.

## Role
- Analyzes complex user requests
- Creates step-by-step execution plans
- Identifies parallelizable subtasks
- Maps dependencies between tasks
- Estimates resource requirements

## When to Use
Call with profile="planner" when you need to:
- Break down a complex task into manageable steps
- Create an execution strategy
- Identify which tasks can run in parallel
- Plan multi-stage operations

## Output Format
The Planner Agent returns structured execution plans that can be passed to the Orchestrator for parallel execution.
