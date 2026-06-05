import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class RecurringTransaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recurring_transactions"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)
    transaction_type: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    amount: Mapped[float] = mapped_column(sa.Numeric(15, 2), nullable=False)
    source_account_id = mapped_column(sa.Uuid, sa.ForeignKey("accounts.id"))
    dest_account_id = mapped_column(sa.Uuid, sa.ForeignKey("accounts.id"))
    category_id = mapped_column(sa.Uuid, sa.ForeignKey("categories.id"))
    payee_id = mapped_column(sa.Uuid, sa.ForeignKey("payees.id"))

    rrule: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    frequency: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    interval_count: Mapped[int] = mapped_column(sa.Integer, default=1)
    day_of_month = mapped_column(sa.Integer)
    day_of_week: Mapped[str | None] = mapped_column(sa.String(20))

    start_date = mapped_column(sa.Date, nullable=False)
    end_date = mapped_column(sa.Date)
    next_occurrence = mapped_column(sa.Date)
    last_occurrence = mapped_column(sa.Date)

    auto_create: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(sa.Text)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)


class Bill(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "bills"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    amount_min: Mapped[float] = mapped_column(sa.Numeric(15, 2), nullable=False)
    amount_max: Mapped[float | None] = mapped_column(sa.Numeric(15, 2))
    date = mapped_column(sa.Date, nullable=False)
    repeat_freq: Mapped[str | None] = mapped_column(sa.String(20))
    payee_id = mapped_column(sa.Uuid, sa.ForeignKey("payees.id"))
    category_id = mapped_column(sa.Uuid, sa.ForeignKey("categories.id"))
    account_id = mapped_column(sa.Uuid, sa.ForeignKey("accounts.id"))
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
