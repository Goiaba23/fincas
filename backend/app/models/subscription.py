import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Subscription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    provider: Mapped[str] = mapped_column(sa.String(50), default="manual")
    provider_subscription_id: Mapped[str | None] = mapped_column(sa.String(255))
    plan_code: Mapped[str] = mapped_column(sa.String(50), default="monthly_40")
    status: Mapped[str] = mapped_column(sa.String(50), default="trial")
    current_period_start = mapped_column(sa.DateTime(timezone=True))
    current_period_end = mapped_column(sa.DateTime(timezone=True))
    trial_started_at = mapped_column(sa.DateTime(timezone=True))
    trial_end = mapped_column(sa.DateTime(timezone=True))
    cancel_at = mapped_column(sa.DateTime(timezone=True))
    canceled_at = mapped_column(sa.DateTime(timezone=True))
