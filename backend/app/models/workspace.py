import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Workspace(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    kind: Mapped[str] = mapped_column(sa.String(20), default="personal")
    icon: Mapped[str | None] = mapped_column(sa.String(50))
    color: Mapped[str | None] = mapped_column(sa.String(7))
    default_currency: Mapped[str] = mapped_column(sa.String(3), default="BRL")
    locale: Mapped[str] = mapped_column(sa.String(10), default="pt-BR")
    is_archived: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    created_by = mapped_column(sa.Uuid, sa.ForeignKey("users.id"), nullable=False)

    members = sa.orm.relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(Base, TimestampMixin):
    __tablename__ = "workspace_members"

    workspace_id: Mapped[str] = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(sa.Uuid, sa.ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(sa.String(20), default="editor")
    invited_by = mapped_column(sa.Uuid, sa.ForeignKey("users.id"))
    joined_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))

    workspace = sa.orm.relationship("Workspace", back_populates="members")
    user = sa.orm.relationship("User", foreign_keys=[user_id])


class WorkspaceMethod(Base, TimestampMixin):
    __tablename__ = "workspace_methods"

    workspace_id: Mapped[str] = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), primary_key=True)
    method: Mapped[str] = mapped_column(sa.String(50), primary_key=True)
    is_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    config: Mapped[dict] = mapped_column(sa.JSON, default={})
