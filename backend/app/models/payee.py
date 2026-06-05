import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Payee(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payees"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(sa.String(255))
    category_id = mapped_column(sa.Uuid, sa.ForeignKey("categories.id"))
    is_merchant: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    logo_url: Mapped[str | None] = mapped_column(sa.Text)
    external_id: Mapped[str | None] = mapped_column(sa.String(255))

    workspace = sa.orm.relationship("Workspace")
