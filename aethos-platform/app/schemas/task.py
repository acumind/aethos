from typing import Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Base schema for Task with common attributes."""
    title: str
    description: Optional[str] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)


class TaskCreate(TaskBase):
    """Schema for creating a new Task."""
    agent_id: int
    owner_id: Optional[int] = None
    status: Optional[str] = "pending"


class TaskUpdate(BaseModel):
    """Schema for updating an existing Task."""
    title: Optional[str] = None
    description: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    azure_task_id: Optional[str] = None
    autogen_task_id: Optional[str] = None
    completed_at: Optional[datetime] = None


class Task(TaskBase):
    """Schema representing a Task."""
    id: int
    agent_id: int
    owner_id: int
    status: str
    output_data: Optional[Dict[str, Any]] = None
    azure_task_id: Optional[str] = None
    autogen_task_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TaskFilter(BaseModel):
    """Schema for filtering Tasks."""
    agent_id: Optional[int] = None
    status: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
