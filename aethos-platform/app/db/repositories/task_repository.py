from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models import Task as TaskModel
from app.schemas.task import TaskCreate, TaskUpdate
from app.db.repositories.base import BaseRepository


class TaskRepository(BaseRepository[TaskModel, TaskCreate, TaskUpdate]):
    """
    Repository for Task model operations.
    """

    def __init__(self, db: Session):
        super().__init__(db, TaskModel)

    def get_tasks_by_owner(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        agent_id: Optional[int] = None
    ) -> List[TaskModel]:
        """
        Get tasks by owner ID with optional filtering.

        Args:
            owner_id: ID of the owner
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter
            agent_id: Optional agent ID filter

        Returns:
            List of Task models
        """
        query = self.db.query(self.model).filter(
            self.model.owner_id == owner_id)

        if status:
            query = query.filter(self.model.status == status)

        if agent_id:
            query = query.filter(self.model.agent_id == agent_id)

        return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_azure_task_id(self, azure_task_id: str) -> Optional[TaskModel]:
        """
        Get a task by Azure Task ID.

        Args:
            azure_task_id: Azure Task ID

        Returns:
            Task model if found, None otherwise
        """
        return (
            self.db.query(self.model)
            .filter(self.model.azure_task_id == azure_task_id)
            .first()
        )

    def get_by_autogen_task_id(self, autogen_task_id: str) -> Optional[TaskModel]:
        """
        Get a task by AutoGen Task ID.

        Args:
            autogen_task_id: AutoGen Task ID

        Returns:
            Task model if found, None otherwise
        """
        return (
            self.db.query(self.model)
            .filter(self.model.autogen_task_id == autogen_task_id)
            .first()
        )

    def complete_task(
        self,
        task_id: int,
        output_data: Dict[str, Any]
    ) -> Optional[TaskModel]:
        """
        Mark a task as completed with output data.

        Args:
            task_id: ID of the task
            output_data: Output data from the task

        Returns:
            Updated Task model
        """
        task = self.get(id=task_id)
        if not task:
            return None

        task_update = TaskUpdate(
            status="completed",
            output_data=output_data,
            completed_at=datetime.utcnow()
        )

        return self.update(db_obj=task, obj_in=task_update)

    def fail_task(
        self,
        task_id: int,
        error: str
    ) -> Optional[TaskModel]:
        """
        Mark a task as failed with error information.

        Args:
            task_id: ID of the task
            error: Error message

        Returns:
            Updated Task model
        """
        task = self.get(id=task_id)
        if not task:
            return None

        task_update = TaskUpdate(
            status="failed",
            output_data={"error": error},
            completed_at=datetime.utcnow()
        )

        return self.update(db_obj=task, obj_in=task_update)

    def get_pending_tasks(self) -> List[TaskModel]:
        """
        Get all pending tasks.

        Returns:
            List of pending Task models
        """
        return (
            self.db.query(self.model)
            .filter(self.model.status == "pending")
            .all()
        )

    def get_running_tasks(self) -> List[TaskModel]:
        """
        Get all running tasks.

        Returns:
            List of running Task models
        """
        return (
            self.db.query(self.model)
            .filter(self.model.status == "running")
            .all()
        )
