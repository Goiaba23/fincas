from app.tasks.worker import celery_app


@celery_app.task
def sync_all_connections():
    """Sync all active bank connections (runs every hour via beat)."""
    return {"synced": 0}


@celery_app.task
def sync_single_connection(connection_id: str):
    """Sync a single bank connection (triggered manually by user)."""
    return {"connection_id": connection_id, "status": "completed"}
