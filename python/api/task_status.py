"""
API endpoint for checking persisted task status.
"""

from python.helpers.api import ApiHandler
from python.helpers.task_persistence import TaskPersistence, BackgroundTaskManager


class TaskStatus(ApiHandler):
    """Get status of persisted/background tasks."""

    async def process(self, input: dict, request) -> dict:
        context_id = input.get("context_id", "")
        task_id = input.get("task_id", "")

        if not context_id:
            return {"error": "context_id is required"}

        persistence = TaskPersistence(context_id)

        if task_id:
            # Get specific task
            task = persistence.load_task(task_id)
            if task:
                return {"task": task.to_dict()}
            else:
                return {"error": f"Task {task_id} not found"}
        else:
            # List all tasks
            tasks = persistence.list_tasks()
            return {
                "tasks": [t.to_dict() for t in tasks],
                "active_count": len([t for t in tasks if t.state.value in ["running", "pending", "paused"]])
            }
