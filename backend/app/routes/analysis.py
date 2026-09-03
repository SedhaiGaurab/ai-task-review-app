from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import TaskModel, AIAnalysisResult
from app.services.ai_service import analyse_task

router = APIRouter(prefix="/tasks", tags=["ai"])


@router.post("/{task_id}/analyse", response_model=AIAnalysisResult)
def analyse_task_endpoint(task_id: str, db: Session = Depends(get_db)):
    """
    Send the task's title and description to the configured OpenRouter model and return a structured
    analysis: category, priority, summary, and recommendedAction.

    Returns 503 if the AI service fails, so the app never crashes on AI errors.
    """
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        result = analyse_task(title=task.title, description=task.description)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI analysis failed: {exc}",
        ) from exc

    return result
