import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class BankConnection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bank_connections"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    user_id = mapped_column(sa.Uuid, sa.ForeignKey("users.id"), nullable=False)
    provider: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    external_item_id: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    external_connector_id: Mapped[str | None] = mapped_column(sa.String(255))
    credentials_encrypted: Mapped[str | None] = mapped_column(sa.Text)
    status: Mapped[str] = mapped_column(sa.String(20), default="connected")
    last_sync_at = mapped_column(sa.DateTime(timezone=True))
    last_sync_error: Mapped[str | None] = mapped_column(sa.Text)
    sync_frequency_min: Mapped[int] = mapped_column(sa.Integer, default=240)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)

    __table_args__ = (sa.UniqueConstraint("provider", "external_item_id"),)


class ImportLog(Base, UUIDMixin):
    __tablename__ = "import_logs"

    connection_id = mapped_column(sa.Uuid, sa.ForeignKey("bank_connections.id"))
    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(20), default="pending")
    transactions_found: Mapped[int] = mapped_column(sa.Integer, default=0)
    transactions_imported: Mapped[int] = mapped_column(sa.Integer, default=0)
    transactions_skipped: Mapped[int] = mapped_column(sa.Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(sa.Text)
    started_at = mapped_column(sa.DateTime(timezone=True))
    completed_at = mapped_column(sa.DateTime(timezone=True))
