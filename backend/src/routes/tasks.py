"""Task API routes with user-scoped endpoints.

Reference: @specs/api/rest-endpoints.md
All endpoints under /api/{user_id}/tasks with JWT authentication.

Reference: @specs/features/task-crud.md
User isolation enforced on all operations.

Reference: @specs/features/event-driven.md (Phase V)
Every Create, Update, Delete publishes event via Dapr.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src import crud
from src.auth import CurrentUser, get_current_user, verify_user_access
from src.database import get_session
from src.events import event_publisher  # Phase V: Dapr events
from src.models import (
    Priority,
    Task,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)

router = APIRouter(prefix="/api/{user_id}", tags=["Tasks"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/tasks", response_model=list[TaskRead])
async def list_tasks(
    user_id: str,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(verify_user_access)],
    completed: bool | None = Query(None, description="Filter by completion status"),
    priority: Priority | None = Query(None, description="Filter by priority"),
    search: str | None = Query(None, description="Search in title/description"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_desc: bool = Query(True, description="Sort descending"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> list[Task]:
    """
    List all tasks for the authenticated user.
    
    Per AC-002.1: Display all tasks belonging to current user.
    Per AC-002.4: Tasks are sorted by creation date (newest first).
    """
    return await crud.get_tasks(
        session=session,
        user_id=user_id,
        completed=completed,
        priority=priority,
        search=search,
        sort_by=sort_by,
        sort_desc=sort_desc,
        skip=skip,
        limit=limit,
    )


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    session: SessionDep,
    task_in: TaskCreate,
    current_user: Annotated[CurrentUser, Depends(verify_user_access)],
) -> Task:
    """
    Create a new task for the authenticated user.
    
    Per AC-001.1: Title is required (1-200 characters).
    Per AC-001.2: Description is optional (max 1000 characters).
    Per AC-001.5: Task is associated with the logged-in user.
    Per AC-001.6: System confirms successful creation.
    
    Phase V: Publishes TaskCreated event via Dapr.
    """
    task = await crud.create_task(session, task_in, user_id=user_id)
    
    # Phase V: Publish event via Dapr sidecar
    await event_publisher.publish_task_created(
        task_id=task.id,
        user_id=user_id,
        title=task.title,
    )
    
    return task


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: str,
    task_id: int,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(verify_user_access)],
) -> Task:
    """Get a specific task for the authenticated user."""
    task = await crud.get_task(session, task_id, user_id=user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: str,
    task_id: int,
    session: SessionDep,
    task_in: TaskUpdate,
    current_user: Annotated[CurrentUser, Depends(verify_user_access)],
) -> Task:
    """
    Update a task for the authenticated user.
    
    Per AC-003.1: Can update title (1-200 characters).
    Per AC-003.2: Can update description (max 1000 characters).
    Per AC-003.3: Cannot update task that doesn't exist.
    Per AC-003.4: Cannot update another user's task.
    Per AC-003.5: System confirms successful update.
    
    Phase V: Publishes TaskUpdated event via Dapr.
    """
    task = await crud.update_task(session, task_id, task_in, user_id=user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Phase V: Publish event via Dapr sidecar
    await event_publisher.publish_task_updated(
        task_id=task.id,
        user_id=user_id,
        title=task.title,
    )
    
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(verify_user_access)],
) -> None:
    """
    Delete a task for the authenticated user.
    
    Per AC-004.1: Task is permanently removed.
    Per AC-004.2: Cannot delete task that doesn't exist.
    Per AC-004.3: Cannot delete another user's task.
    Per AC-004.4: System confirms successful deletion.
    
    Phase V: Publishes TaskDeleted event via Dapr.
    """
    # Get task title before deletion for event
    task = await crud.get_task(session, task_id, user_id=user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    title = task.title
    success = await crud.delete_task(session, task_id, user_id=user_id)
    
    if success:
        # Phase V: Publish event via Dapr sidecar
        await event_publisher.publish_task_deleted(
            task_id=task_id,
            user_id=user_id,
            title=title,
        )


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_complete(
    user_id: str,
    task_id: int,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(verify_user_access)],
) -> Task:
    """
    Toggle task completion status for the authenticated user.
    
    Per AC-005.1: Toggle task between complete/incomplete.
    Per AC-005.3: Cannot toggle task that doesn't exist.
    Per AC-005.4: Cannot toggle another user's task.
    Per AC-005.5: System confirms status change.
    """
    task = await crud.toggle_task_complete(session, task_id, user_id=user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/stats")
async def get_stats(
    user_id: str,
    session: SessionDep,
    current_user: Annotated[CurrentUser, Depends(verify_user_access)],
) -> dict[str, int]:
    """Get task statistics for the authenticated user."""
    return await crud.get_task_stats(session, user_id=user_id)
