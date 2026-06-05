import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Goal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "goals"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    target_amount: Mapped[float] = mapped_column(sa.Numeric(15, 2), nullable=False)
    current_amount: Mapped[float] = mapped_column(sa.Numeric(15, 2), default=0)
    target_date = mapped_column(sa.Date)
    account_id = mapped_column(sa.Uuid, sa.ForeignKey("accounts.id"))
    category_id = mapped_column(sa.Uuid, sa.ForeignKey("categories.id"))
    is_piggy_bank: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    completed_at = mapped_column(sa.DateTime(timezone=True))
