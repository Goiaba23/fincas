import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin


class Attachment(Base, UUIDMixin):
    __tablename__ = "attachments"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    attachable_id = mapped_column(sa.Uuid, nullable=False)
    attachable_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    filename: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(sa.String(100))
    size_bytes = mapped_column(sa.Integer)
    storage_path: Mapped[str] = mapped_column(sa.Text, nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    created_by = mapped_column(sa.Uuid, sa.ForeignKey("users.id"))
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))
