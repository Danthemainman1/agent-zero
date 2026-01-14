## Tool: "orchestrate" - Multi-Agent Task Orchestration

Use this tool to execute complex tasks using a coordinated team of specialized AI agents working in parallel.

### How it works:
1. **Planner Agent** analyzes your task and breaks it into subtasks
2. **Executor Agents** work on independent subtasks in parallel
3. **Verifier Agent** checks the quality of all results

### When to use:
- Complex multi-step tasks that can be parallelized
- Research tasks requiring multiple sources
- Development tasks with independent components
- Any task that would benefit from divide-and-conquer

### Arguments:
- **task** (required): The complex task description
- **mode** (optional): Execution strategy
  - `"auto"` - Automatically choose best strategy (default)
  - `"parallel"` - Force parallel execution of all independent subtasks
  - `"sequential"` - Execute subtasks one at a time
  - `"plan_only"` - Only create the plan, don't execute

### Usage examples:

**Parallel research:**
~~~json
{
    "thoughts": ["This research task has multiple independent topics that can be investigated simultaneously..."],
    "tool_name": "orchestrate",
    "tool_args": {
        "task": "Research and compare the top 5 cloud providers: AWS, Azure, GCP, Oracle Cloud, and IBM Cloud. For each, analyze pricing, features, and market share.",
        "mode": "parallel"
    }
}
~~~

**Complex development:**
~~~json
{
    "thoughts": ["This project has multiple independent components - frontend, backend, and database setup can be done in parallel..."],
    "tool_name": "orchestrate",
    "tool_args": {
        "task": "Create a full-stack todo application with React frontend, Node.js API, and PostgreSQL database",
        "mode": "auto"
    }
}
~~~

**Planning only:**
~~~json
{
    "thoughts": ["I want to see the execution plan before committing to full execution..."],
    "tool_name": "orchestrate",
    "tool_args": {
        "task": "Redesign the company website with new branding",
        "mode": "plan_only"
    }
}
~~~

### Benefits:
- **Faster execution** through parallelization
- **Better quality** through specialized agents
- **Verified results** through dedicated verification step
- **Transparency** with detailed execution logging
