import logging
import datetime as dt

from app.celery_app import celery_app

logger = logging.getLogger("app")

@celery_app.task
def nightly_maintenance() -> str:
    """
    Example periodic task.
    In a real system, you could:
      - clean old data
      - recompute aggregates
      - send daily summaries, etc.
    """
    now = dt.datetime.now().isoformat()
    logger.info(f"[Celery] Running nightly_maintenance at {now}")
    return f"Nightly maintenance run at {now}"