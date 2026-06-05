import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class CategoryGroup(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "category_groups"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0)
    is_income: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    color: Mapped[str | None] = mapped_column(sa.String(7))

    categories = sa.orm.relationship("Category", back_populates="group", cascade="all, delete-orphan")


class Category(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "categories"

    group_id = mapped_column(sa.Uuid, sa.ForeignKey("category_groups.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0)
    is_hidden: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    color: Mapped[str | None] = mapped_column(sa.String(7))

    group = sa.orm.relationship("CategoryGroup", back_populates="categories")
