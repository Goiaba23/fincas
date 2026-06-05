import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Budget(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "budgets"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    budget_type: Mapped[str] = mapped_column(sa.String(20), default="envelope")
    currency_code: Mapped[str] = mapped_column(sa.String(3), sa.ForeignKey("currencies.code"))
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)

    monthly_income = mapped_column(sa.Numeric(15, 2), default=0)
    ready_to_assign = mapped_column(sa.Numeric(15, 2), default=0)
    last_month_calculated = mapped_column(sa.String(7))

    limits = sa.orm.relationship("BudgetLimit", back_populates="budget", cascade="all, delete-orphan")


class BudgetLimit(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "budget_limits"

    budget_id = mapped_column(sa.Uuid, sa.ForeignKey("budgets.id"), nullable=False)
    category_id = mapped_column(sa.Uuid, sa.ForeignKey("categories.id"), nullable=False)
    amount: Mapped[float] = mapped_column(sa.Numeric(15, 2), nullable=False)
    period: Mapped[str] = mapped_column(sa.String(20), default="monthly")
    start_date = mapped_column(sa.Date, nullable=False)
    end_date = mapped_column(sa.Date)
    is_carryover: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    assigned = mapped_column(sa.Numeric(15, 2), default=0)
    activity = mapped_column(sa.Numeric(15, 2), default=0)
    available = mapped_column(sa.Numeric(15, 2), default=0)

    budget = sa.orm.relationship("Budget", back_populates="limits")
    category = sa.orm.relationship("Category")


class EnvelopeAssignment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "envelope_assignments"

    budget_id = mapped_column(sa.Uuid, sa.ForeignKey("budgets.id"), nullable=False)
    category_id = mapped_column(sa.Uuid, sa.ForeignKey("categories.id"), nullable=False)
    month = mapped_column(sa.String(7), nullable=False)
    assigned_amount = mapped_column(sa.Numeric(15, 2), default=0)
    carryover_amount = mapped_column(sa.Numeric(15, 2), default=0)

    budget = sa.orm.relationship("Budget")
