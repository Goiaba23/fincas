from app.tasks.worker import celery_app


@celery_app.task
def process_recurring_transactions():
    """Create transactions from recurring rules that are due."""
    return {"created": 0}
