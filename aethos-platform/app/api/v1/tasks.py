from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repositories.task_repository import TaskRepository
from app.db.repositories.agent_repository import AgentRepository
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.core.security import get_current_user
from app.schemas.auth import User
from app.services.azure_ai_service import AzureAIService
from app.services.autogen_service import AutogenService

router = APIRouter()
ai_service = AzureAIService()
autogen_service = AutogenService()


@router.get("/", response_model=List[Task])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    agent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve tasks with optional filtering.
    """
    repository = TaskRepository(db)
    tasks = repository.get_tasks_by_owner(
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        agent_id=agent_id
    )
    return tasks


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task and execute it.
    """
    # Validate agent exists
    agent_repository = AgentRepository(db)
    agent = agent_repository.get(id=task_in.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Validate agent belongs to user
    if agent.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Create task in database
    task_repository = TaskRepository(db)
    task = task_repository.create(
        obj_in=TaskCreate(
            **task_in.dict(),
            owner_id=current_user.id,
            status="pending"
        )
    )

    # Execute task in background
    background_tasks.add_task(
        execute_task,
        task_id=task.id,
        agent=agent,
        task_input=task_in.input_data,
        db=db
    )

    return task


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific task by ID.
    """
    repository = TaskRepository(db)
    task = repository.get(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task.
    """
    repository = TaskRepository(db)
    task = repository.get(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    repository.remove(id=task_id)
    return None


@router.post("/{task_id}/cancel", response_model=Task)
async def cancel_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a running task.
    """
    repository = TaskRepository(db)
    task = repository.get(id=task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Only pending or running tasks can be canceled
    if task.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Task cannot be canceled as it is in {task.status} state"
        )

    # Cancel task in Azure AI service if needed
    if task.azure_task_id:
        try:
            await ai_service.cancel_task(task.azure_task_id)
        except Exception as e:
            # Log error but continue
            pass

    # Cancel task in AutoGen service if needed
    if task.autogen_task_id:
        try:
            await autogen_service.cancel_task(task.autogen_task_id)
        except Exception as e:
            # Log error but continue
            pass

    # Update task status
    task = repository.update(
        db_obj=task,
        obj_in=TaskUpdate(status="canceled")
    )

    return task


async def execute_task(task_id: int, agent, task_input, db: Session):
    """
    Background task to execute a task.

    Args:
        task_id: The ID of the task to execute
        agent: The agent to use for execution
        task_input: The input data for the task
        db: Database session
    """
    repository = TaskRepository(db)
    task = repository.get(id=task_id)

    if not task:
        return

    # Update task status to running
    task = repository.update(
        db_obj=task,
        obj_in=TaskUpdate(status="running")
    )

    try:
        # Execute task in Azure AI service
        azure_response = await ai_service.execute_agent_task(
            agent_id=agent.azure_agent_id,
            task_data=task_input
        )

        # Execute task in AutoGen service
        autogen_response = await autogen_service.execute_task(
            agent_id=agent.autogen_agent_id,
            message=task_input.get("message", ""),
            task_config=task_input.get("config", {})
        )

        # Save task IDs for tracking
        task = repository.update(
            db_obj=task,
            obj_in=TaskUpdate(
                azure_task_id=azure_response.get("taskId"),
                autogen_task_id=autogen_response.get("task_id")
            )
        )

        # Poll for task completion
        azure_result = await poll_azure_task(azure_response.get("taskId"))
        autogen_result = await poll_autogen_task(autogen_response.get("task_id"))

        # Combine results
        combined_result = {
            "azure": azure_result,
            "autogen": autogen_result
        }

        # Update task with results
        task = repository.update(
            db_obj=task,
            obj_in=TaskUpdate(
                status="completed",
                output_data=combined_result
            )
        )

    except Exception as e:
        # Update task as failed
        task = repository.update(
            db_obj=task,
            obj_in=TaskUpdate(
                status="failed",
                output_data={"error": str(e)}
            )
        )


async def poll_azure_task(task_id: str):
    """
    Poll Azure AI service for task completion.

    Args:
        task_id: The Azure task ID to poll

    Returns:
        Task result
    """
    if not task_id:
        return None

    # In real implementation, use exponential backoff and proper polling
    # This is simplified for example purposes
    try:
        status = await ai_service.get_task_status(task_id)
        while status.get("status") == "running":
            # Wait and check again
            import asyncio
            await asyncio.sleep(5)
            status = await ai_service.get_task_status(task_id)

        return status.get("result")
    except Exception as e:
        return {"error": str(e)}


async def poll_autogen_task(task_id: str):
    """
    Poll AutoGen service for task completion.

    Args:
        task_id: The AutoGen task ID to poll

    Returns:
        Task result
    """
    if not task_id:
        return None

    # In real implementation, use exponential backoff and proper polling
    # This is simplified for example purposes
    try:
        status = await autogen_service.get_task_status(task_id)
        while status.get("status") == "running":
            # Wait and check again
            import asyncio
            await asyncio.sleep(5)
            status = await autogen_service.get_task_status(task_id)

        return status.get("result")
    except Exception as e:
        return {"error": str(e)}
