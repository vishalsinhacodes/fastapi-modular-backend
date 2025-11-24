from fastapi import APIRouter, Depends
from celery.result import AsyncResult

from app.celery_app import celery_app
from app.models.user import UserModel
from app.core.security import get_current_user
from app.tasks.email_tasks import send_welcome_email

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/send-welcome-email")
def trigger_welcome_email(
    current_user: UserModel = Depends(get_current_user)
):
    task = send_welcome_email.delay(current_user.email)
    return {
        "message": "Task queued",
        "task_id": task.id,
    }
    
@router.get("/{task_id}")
def get_task_status(task_id: str):
    """Check status/result of a Celery task."""
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.successful() else None,
    }