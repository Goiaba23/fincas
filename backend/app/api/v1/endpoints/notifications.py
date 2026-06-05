from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.notification import Notification, NotificationChannel

router = APIRouter(prefix="/notifications", tags=["notifications"])


class ChannelUpdate(BaseModel):
    channel: str
    is_enabled: bool


@router.get("/")
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Notification)
        .where(
            Notification.user_id == user.id,
            Notification.is_read == False,
        )
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    notifications = result.scalars().all()
    return [
        {
            "id": str(n.id),
            "type": n.type,
            "title": n.title,
            "body": n.body,
            "data": n.data,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifications
    ]


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await db.execute(
        update(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
        .values(is_read=True)
    )
    return {"status": "ok"}


@router.post("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await db.execute(
        update(Notification)
        .where(
            Notification.user_id == user.id,
            Notification.is_read == False,
        )
        .values(is_read=True)
    )
    return {"status": "ok"}


@router.get("/channels")
async def get_channels(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NotificationChannel).where(NotificationChannel.user_id == user.id)
    )
    channels = result.scalars().all()
    return [
        {"channel": c.channel, "enabled": c.is_enabled}
        for c in channels
    ]


@router.post("/channels")
async def update_channel(
    req: ChannelUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NotificationChannel).where(
            NotificationChannel.user_id == user.id,
            NotificationChannel.channel == req.channel,
        )
    )
    channel = result.scalar_one_or_none()
    if channel:
        channel.is_enabled = req.is_enabled
    else:
        channel = NotificationChannel(
            user_id=user.id,
            channel=req.channel,
            is_enabled=req.is_enabled,
        )
        db.add(channel)

    return {"channel": req.channel, "enabled": req.is_enabled}
