import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin


class NotificationChannel(Base):
    __tablename__ = "notification_channels"

    user_id = mapped_column(sa.Uuid, sa.ForeignKey("users.id"), primary_key=True)
    channel: Mapped[str] = mapped_column(sa.String(50), primary_key=True)
    is_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    config = mapped_column(sa.JSON, default=dict)


class Notification(Base, UUIDMixin):
    __tablename__ = "notifications"

    user_id = mapped_column(sa.Uuid, sa.ForeignKey("users.id"), nullable=False)
    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"))
    type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(sa.Text)
    data = mapped_column(sa.JSON)
    is_read: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    read_at = mapped_column(sa.DateTime(timezone=True))
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))
