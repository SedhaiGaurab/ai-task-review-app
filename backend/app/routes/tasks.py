import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import (
    TaskModel,
    TaskCreate,
    TaskStatusUpdate,
    TaskResponse,
    TaskStatus,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter tasks by status"),
    db: Session = Depends(get_db),
):
    """Return all tasks, optionally filtered by status."""
    query = db.query(TaskModel)
    if status:
        query = query.filter(TaskModel.status == status)
    tasks = query.order_by(TaskModel.created_at.desc()).all()
    return [TaskResponse.from_orm_model(t) for t in tasks]


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    task = TaskModel(
        id=str(uuid.uuid4()),
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status=TaskStatus.NEW,
        created_at=datetime.now(timezone.utc),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskResponse.from_orm_model(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Retrieve a single task by ID."""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_orm_model(task)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """Delete a task permanently."""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: str,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the status of a task.
    Only accepts NEW | IN_PROGRESS | COMPLETED — FastAPI validates via the enum,
    so invalid values are automatically rejected with a 422 response.
    """
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = payload.status
    db.commit()
    db.refresh(task)
    return TaskResponse.from_orm_model(task)
