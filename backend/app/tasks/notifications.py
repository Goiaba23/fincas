from app.tasks.worker import celery_app


@celery_app.task
def generate_bill_reminders():
    """Check for upcoming bills and generate notifications."""
    return {"notifications": 0}
