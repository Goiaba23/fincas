import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class CreditCardBill(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "credit_card_bills"

    account_id = mapped_column(sa.Uuid, sa.ForeignKey("accounts.id"), nullable=False)
    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    closing_date = mapped_column(sa.Date, nullable=False)
    due_date = mapped_column(sa.Date, nullable=False)
    total_amount: Mapped[float] = mapped_column(sa.Numeric(15, 2), default=0)
    minimum_payment: Mapped[float | None] = mapped_column(sa.Numeric(15, 2))
    paid_amount: Mapped[float] = mapped_column(sa.Numeric(15, 2), default=0)
    status: Mapped[str] = mapped_column(sa.String(20), default="open")
    is_closed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    paid_at = mapped_column(sa.DateTime(timezone=True))
    external_id: Mapped[str | None] = mapped_column(sa.String(255))
