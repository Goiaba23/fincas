from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.bank import BankConnection, ImportLog
from app.providers.bank.pluggy import get_provider

router = APIRouter(prefix="/bank", tags=["bank_sync"])


class ConnectRequest(BaseModel):
    provider: str = "pluggy"


class CallbackRequest(BaseModel):
    item_id: str
    provider: str = "pluggy"


@router.post("/connect")
async def get_connect_token(
    req: ConnectRequest,
    user: User = Depends(get_current_user),
):
    try:
        provider = get_provider(req.provider)
    except ValueError as e:
        raise HTTPException(400, str(e))

    token = await provider.create_connect_token(str(user.id))
    return {"connect_token": token}


@router.post("/callback")
async def handle_callback(
    req: CallbackRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        provider = get_provider(req.provider)
    except ValueError as e:
        raise HTTPException(400, str(e))

    connection_data = await provider.process_callback(req.item_id)

    conn = BankConnection(
        user_id=user.id,
        provider=req.provider,
        external_item_id=connection_data.item_id,
        status=connection_data.status,
    )
    db.add(conn)

    return {"id": str(conn.id), "status": conn.status}


@router.get("/connections")
async def list_connections(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(BankConnection).where(BankConnection.is_active == True)
    )
    connections = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "provider": c.provider,
            "status": c.status,
            "last_sync": c.last_sync_at.isoformat() if c.last_sync_at else None,
            "sync_frequency_min": c.sync_frequency_min,
        }
        for c in connections
    ]


@router.post("/connections/{connection_id}/sync")
async def trigger_sync(
    connection_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(BankConnection).where(BankConnection.id == connection_id)
    )
    conn = result.scalar_one_or_none()
    if not conn:
        raise HTTPException(404)

    try:
        provider = get_provider(conn.provider)
        await provider.refresh_connection(conn.external_item_id)
        conn.last_sync_at = None  # will be updated by background task

        return {"id": str(conn.id), "status": "syncing"}
    except Exception as e:
        conn.status = "error"
        conn.last_sync_error = str(e)
        return {"id": str(conn.id), "status": "error", "error": str(e)}


@router.get("/logs")
async def import_logs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ImportLog).order_by(ImportLog.created_at.desc()).limit(20)
    )
    logs = result.scalars().all()
    return [
        {
            "id": str(l.id),
            "status": l.status,
            "found": l.transactions_found,
            "imported": l.transactions_imported,
            "skipped": l.transactions_skipped,
            "error": l.error_message,
            "started_at": l.started_at.isoformat() if l.started_at else None,
        }
        for l in logs
    ]
