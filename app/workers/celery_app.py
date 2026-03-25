from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "github_crawler",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.workers"])

# Configure Celery Beat Schedule
celery_app.conf.beat_schedule = {
    "daily-crawl-task": {
        "task": "app.workers.tasks.crawl_repositories_task",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight UTC
        "args": (100000,),
    },
}
