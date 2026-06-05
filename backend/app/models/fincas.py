import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class KakeiboEntry(Base, UUIDMixin):
    __tablename__ = "kakeibo_entries"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    user_id = mapped_column(sa.Uuid, sa.ForeignKey("users.id"), nullable=False)
    week_start = mapped_column(sa.Date, nullable=False)
    total_income = mapped_column(sa.Numeric(15, 2))
    total_expenses = mapped_column(sa.Numeric(15, 2))
    savings_amount = mapped_column(sa.Numeric(15, 2))
    q1_available: Mapped[str | None]
    q2_save_goal: Mapped[str | None]
    q3_spending: Mapped[str | None]
    q4_improve: Mapped[str | None]
    reflection: Mapped[str | None]
    mood: Mapped[str | None]
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))

    spending = sa.orm.relationship("KakeiboSpending", back_populates="entry", cascade="all, delete-orphan")


class KakeiboSpending(Base, UUIDMixin):
    __tablename__ = "kakeibo_spending"

    entry_id = mapped_column(sa.Uuid, sa.ForeignKey("kakeibo_entries.id"), nullable=False)
    category: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    description: Mapped[str | None]
    amount: Mapped[float] = mapped_column(sa.Numeric(15, 2), nullable=False)
    journal_id = mapped_column(sa.Uuid, sa.ForeignKey("transaction_journals.id"))
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))

    entry = sa.orm.relationship("KakeiboEntry", back_populates="spending")


class MicroSaving(Base, UUIDMixin):
    __tablename__ = "micro_savings"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    savings_type: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    amount = mapped_column(sa.Numeric(15, 2))
    percentage = mapped_column(sa.Numeric(5, 2))
    source_account_id = mapped_column(sa.Uuid, sa.ForeignKey("accounts.id"))
    target_account_id = mapped_column(sa.Uuid, sa.ForeignKey("accounts.id"))
    goal_id = mapped_column(sa.Uuid, sa.ForeignKey("goals.id"))
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    run_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    total_saved = mapped_column(sa.Numeric(15, 2), default=0)
    last_run_at = mapped_column(sa.DateTime(timezone=True))
    config = mapped_column(sa.JSON, default={})
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))


class MicroSavingsLog(Base, UUIDMixin):
    __tablename__ = "micro_savings_log"

    micro_savings_id = mapped_column(sa.Uuid, sa.ForeignKey("micro_savings.id"), nullable=False)
    amount = mapped_column(sa.Numeric(15, 2), nullable=False)
    journal_id = mapped_column(sa.Uuid, sa.ForeignKey("transaction_journals.id"))
    executed_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))
