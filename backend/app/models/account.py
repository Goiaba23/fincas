import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Account(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "accounts"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    account_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    currency_code: Mapped[str] = mapped_column(sa.String(3), default="BRL")
    balance: Mapped[float] = mapped_column(sa.Numeric(15, 2), default=0)
    balance_date = mapped_column(sa.Date, server_default=sa.text("CURRENT_DATE"))
    is_archived: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    is_off_budget: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    credit_limit = mapped_column(sa.Numeric(15, 2))
    statement_close_day = mapped_column(sa.Integer)
    statement_due_day = mapped_column(sa.Integer)
    card_brand: Mapped[str | None] = mapped_column(sa.String(50))
    card_last_digits: Mapped[str | None] = mapped_column(sa.String(4))

    external_id: Mapped[str | None] = mapped_column(sa.String(255))
    external_item_id: Mapped[str | None] = mapped_column(sa.String(255))
    connector_provider: Mapped[str | None] = mapped_column(sa.String(50))
    last_sync_at = mapped_column(sa.DateTime(timezone=True))

    color: Mapped[str | None] = mapped_column(sa.String(7))
    icon: Mapped[str | None] = mapped_column(sa.String(50))
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0)

    workspace = sa.orm.relationship("Workspace")
