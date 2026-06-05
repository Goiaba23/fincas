from app.tasks.worker import celery_app


@celery_app.task
def update_exchange_rates():
    """Fetch latest exchange rates from BCB PTAX."""
    return {"updated": 0}
