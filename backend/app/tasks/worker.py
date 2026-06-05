from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "fincas",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    beat_schedule={
        "sync-bank-accounts": {
            "task": "app.tasks.bank_sync.sync_all_connections",
            "schedule": 3600.0,
        },
        "process-recurring": {
            "task": "app.tasks.recurring.process_recurring_transactions",
            "schedule": 3600.0,
        },
        "update-exchange-rates": {
            "task": "app.tasks.exchange.update_exchange_rates",
            "schedule": 86400.0,
        },
        "generate-notifications": {
            "task": "app.tasks.notifications.generate_bill_reminders",
            "schedule": 43200.0,
        },
    },
)


@celery_app.task
def health_check():
    return {"status": "ok"}
