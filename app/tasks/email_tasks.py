import logging
import time

from app.celery_app import celery_app

logger = logging.getLogger("app")

@celery_app.task
def send_welcome_email(email: str) -> str:
    
    logger.info(f"[Celery] Starting send_welcome_email for {email}")
    
    time.sleep(5)
    
    logger.info(f"[Celery] Finished send_welcome_email for {email}")
    return f"Welcome email send to {email}"