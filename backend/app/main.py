import uuid
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, SessionLocal, Base
from app.models.task import TaskModel, TaskStatus, TaskPriority
from app.routes import analysis, tasks

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Assisted Task Review API",
    version="1.0.0",
    description="Backend for the AI-Assisted Task Review application.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(tasks.router)
app.include_router(analysis.router)


SEED_TASKS = [
    {
        "title": "Buy groceries",
        "description": "Pick up milk, eggs, fruit, and bread after work.",
        "priority": TaskPriority.MEDIUM,
        "status": TaskStatus.IN_PROGRESS,
    },
    {
        "title": "Finish the project report",
        "description": "Review the final section and send the report to the team.",
        "priority": TaskPriority.LOW,
        "status": TaskStatus.COMPLETED,
    },
    {
        "title": "Water the plants",
        "description": "Give the indoor plants some water on Sunday morning.",
        "priority": TaskPriority.MEDIUM,
        "status": TaskStatus.NEW,
    },
]


@app.on_event("startup")
def seed_database():
    """Insert sample tasks on first run so the UI has data immediately."""
    db = SessionLocal()
    try:
        if db.query(TaskModel).count() == 0:
            for data in SEED_TASKS:
                db.add(
                    TaskModel(
                        id=str(uuid.uuid4()),
                        title=data["title"],
                        description=data["description"],
                        priority=data["priority"],
                        status=data["status"],
                        created_at=datetime.now(timezone.utc),
                    )
                )
            db.commit()
    finally:
        db.close()

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
