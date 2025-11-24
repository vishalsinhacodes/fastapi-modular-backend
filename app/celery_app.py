from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "fastapi_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.maintenance_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Celery Beat schedule (periodic tasks)
celery_app.conf.beat_schedule = {
    "nightly-maintenance-job": {
        "task": "app.tasks.maintenance_tasks.nightly_maintenance",
        "schedule": 60.0 * 60.0 * 24.0 # run once every 24 hours
    }
    
}