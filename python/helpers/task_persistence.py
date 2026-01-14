"""
Task Persistence System for continuous operation and session recovery.
Persists running tasks to survive disconnections and enable notifications on completion.
"""

import json
import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum

from python.helpers import files
from python.helpers.print_style import PrintStyle


class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PersistedTask:
    """Represents a persistable task."""
    id: str
    context_id: str
    name: str
    description: str
    state: TaskState = TaskState.PENDING
    progress: float = 0.0
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    notify_on_complete: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["state"] = self.state.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersistedTask":
        """Create from dictionary."""
        data["state"] = TaskState(data.get("state", "pending"))
        return cls(**data)


class TaskPersistence:
    """
    Manages task persistence for continuous operation.
    Enables tasks to survive disconnections and notify on completion.
    """

    TASKS_DIR = "tmp/persisted_tasks"

    def __init__(self, context_id: str):
        self.context_id = context_id
        self.tasks_dir = files.get_abs_path(self.TASKS_DIR, context_id)
        self._ensure_dir()

    def _ensure_dir(self):
        """Ensure tasks directory exists."""
        os.makedirs(self.tasks_dir, exist_ok=True)

    def _task_file(self, task_id: str) -> str:
        """Get path to task file."""
        return os.path.join(self.tasks_dir, f"{task_id}.json")

    def create_task(self, 
                    name: str, 
                    description: str,
                    notify_on_complete: bool = True,
                    metadata: Dict[str, Any] = None) -> PersistedTask:
        """Create and persist a new task."""
        import uuid
        
        task = PersistedTask(
            id=str(uuid.uuid4())[:8],
            context_id=self.context_id,
            name=name,
            description=description,
            notify_on_complete=notify_on_complete,
            metadata=metadata or {}
        )
        
        self._save_task(task)
        PrintStyle(font_color="#27AE60").print(f"📋 Task created: {task.id} - {name}")
        
        return task

    def _save_task(self, task: PersistedTask):
        """Save task to disk."""
        task.updated_at = datetime.now().isoformat()
        file_path = self._task_file(task.id)
        
        with open(file_path, "w") as f:
            json.dump(task.to_dict(), f, indent=2)

    def load_task(self, task_id: str) -> Optional[PersistedTask]:
        """Load a task from disk."""
        file_path = self._task_file(task_id)
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            return PersistedTask.from_dict(data)
        except Exception as e:
            PrintStyle.error(f"Failed to load task {task_id}: {e}")
            return None

    def update_progress(self, task_id: str, progress: float, message: str = ""):
        """Update task progress."""
        task = self.load_task(task_id)
        if not task:
            return
            
        task.progress = min(max(0.0, progress), 100.0)
        task.state = TaskState.RUNNING
        
        if message:
            task.checkpoints.append({
                "time": datetime.now().isoformat(),
                "progress": progress,
                "message": message
            })
        
        self._save_task(task)

    def add_checkpoint(self, task_id: str, checkpoint_data: Dict[str, Any]):
        """Add a checkpoint for recovery."""
        task = self.load_task(task_id)
        if not task:
            return
            
        checkpoint = {
            "time": datetime.now().isoformat(),
            **checkpoint_data
        }
        task.checkpoints.append(checkpoint)
        self._save_task(task)

    def complete_task(self, task_id: str, result: str = ""):
        """Mark task as completed."""
        task = self.load_task(task_id)
        if not task:
            return
            
        task.state = TaskState.COMPLETED
        task.progress = 100.0
        task.result = result
        task.completed_at = datetime.now().isoformat()
        
        self._save_task(task)
        PrintStyle(font_color="#27AE60", bold=True).print(f"✅ Task completed: {task.id} - {task.name}")
        
        # Trigger notification if enabled
        if task.notify_on_complete:
            self._notify_completion(task)

    def fail_task(self, task_id: str, error: str):
        """Mark task as failed."""
        task = self.load_task(task_id)
        if not task:
            return
            
        task.state = TaskState.FAILED
        task.error = error
        task.completed_at = datetime.now().isoformat()
        
        self._save_task(task)
        PrintStyle(font_color="#E74C3C", bold=True).print(f"❌ Task failed: {task.id} - {error}")
        
        # Trigger notification
        if task.notify_on_complete:
            self._notify_failure(task)

    def cancel_task(self, task_id: str):
        """Cancel a task."""
        task = self.load_task(task_id)
        if not task:
            return
            
        task.state = TaskState.CANCELLED
        task.completed_at = datetime.now().isoformat()
        
        self._save_task(task)
        PrintStyle(font_color="#F39C12").print(f"🚫 Task cancelled: {task.id}")

    def pause_task(self, task_id: str):
        """Pause a task."""
        task = self.load_task(task_id)
        if not task:
            return
            
        task.state = TaskState.PAUSED
        self._save_task(task)

    def resume_task(self, task_id: str):
        """Resume a paused task."""
        task = self.load_task(task_id)
        if not task:
            return
            
        if task.state == TaskState.PAUSED:
            task.state = TaskState.RUNNING
            self._save_task(task)

    def list_tasks(self, state: TaskState = None) -> List[PersistedTask]:
        """List all tasks, optionally filtered by state."""
        tasks = []
        
        if not os.path.exists(self.tasks_dir):
            return tasks
            
        for filename in os.listdir(self.tasks_dir):
            if filename.endswith(".json"):
                task_id = filename[:-5]
                task = self.load_task(task_id)
                if task:
                    if state is None or task.state == state:
                        tasks.append(task)
        
        # Sort by created_at descending
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks

    def get_active_tasks(self) -> List[PersistedTask]:
        """Get all running or pending tasks."""
        all_tasks = self.list_tasks()
        return [t for t in all_tasks if t.state in [TaskState.RUNNING, TaskState.PENDING, TaskState.PAUSED]]

    def cleanup_completed(self, max_age_hours: int = 24):
        """Remove completed tasks older than max_age_hours."""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        removed = 0
        
        for task in self.list_tasks():
            if task.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]:
                completed_at = datetime.fromisoformat(task.completed_at) if task.completed_at else None
                if completed_at and completed_at < cutoff:
                    file_path = self._task_file(task.id)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        removed += 1
        
        if removed > 0:
            PrintStyle.info(f"Cleaned up {removed} old tasks")

    def _notify_completion(self, task: PersistedTask):
        """Send completion notification."""
        try:
            from agent import AgentContext
            notification_manager = AgentContext.get_notification_manager()
            
            notification_manager.create(
                title=f"Task Completed: {task.name}",
                message=task.result[:200] if task.result else "Task completed successfully",
                notification_type="success",
                context_id=self.context_id
            )
        except Exception as e:
            PrintStyle.warning(f"Failed to send completion notification: {e}")

    def _notify_failure(self, task: PersistedTask):
        """Send failure notification."""
        try:
            from agent import AgentContext
            notification_manager = AgentContext.get_notification_manager()
            
            notification_manager.create(
                title=f"Task Failed: {task.name}",
                message=task.error[:200] if task.error else "Task failed",
                notification_type="error",
                context_id=self.context_id
            )
        except Exception as e:
            PrintStyle.warning(f"Failed to send failure notification: {e}")

    def get_recovery_checkpoint(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest checkpoint for task recovery."""
        task = self.load_task(task_id)
        if not task or not task.checkpoints:
            return None
        
        return task.checkpoints[-1]


class BackgroundTaskManager:
    """
    Manages background tasks that continue running after user disconnection.
    """

    _instance = None
    _tasks: Dict[str, asyncio.Task] = {}

    @classmethod
    def get_instance(cls) -> "BackgroundTaskManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start_background_task(self, 
                              context_id: str,
                              name: str,
                              coro,
                              notify_on_complete: bool = True) -> str:
        """Start a background task that persists."""
        persistence = TaskPersistence(context_id)
        task = persistence.create_task(name, "Background task", notify_on_complete)
        
        async def wrapper():
            try:
                persistence.update_progress(task.id, 0, "Starting...")
                result = await coro
                persistence.complete_task(task.id, str(result) if result else "Completed")
                return result
            except Exception as e:
                persistence.fail_task(task.id, str(e))
                raise

        asyncio_task = asyncio.create_task(wrapper())
        self._tasks[task.id] = asyncio_task
        
        return task.id

    def cancel_background_task(self, task_id: str, context_id: str):
        """Cancel a background task."""
        if task_id in self._tasks:
            self._tasks[task_id].cancel()
            del self._tasks[task_id]
        
        persistence = TaskPersistence(context_id)
        persistence.cancel_task(task_id)

    def get_task_status(self, task_id: str, context_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a background task."""
        persistence = TaskPersistence(context_id)
        task = persistence.load_task(task_id)
        
        if not task:
            return None
            
        return {
            "id": task.id,
            "name": task.name,
            "state": task.state.value,
            "progress": task.progress,
            "result": task.result,
            "error": task.error
        }
