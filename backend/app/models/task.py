import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, String
from pydantic import BaseModel, ConfigDict

from app.database import Base

class TaskStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(String, nullable=False, default=TaskPriority.MEDIUM)
    status = Column(String, nullable=False, default=TaskStatus.NEW)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    createdAt: datetime

    @classmethod
    def from_orm_model(cls, obj: TaskModel) -> "TaskResponse":
        return cls(
            id=obj.id,
            title=obj.title,
            description=obj.description,
            priority=obj.priority,
            status=obj.status,
            createdAt=obj.created_at,
        )


class AIAnalysisResult(BaseModel):
    category: str
    priority: str
    summary: str
    recommendedAction: str
