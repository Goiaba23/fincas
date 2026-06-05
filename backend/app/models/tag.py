import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Tag(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tags"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    color: Mapped[str | None] = mapped_column(sa.String(7))

    __table_args__ = (sa.UniqueConstraint("workspace_id", "name"),)


# Association table for tags <-> journals
class JournalTag(Base):
    __tablename__ = "journal_tag"

    journal_id = mapped_column(sa.Uuid, sa.ForeignKey("transaction_journals.id"), primary_key=True)
    tag_id = mapped_column(sa.Uuid, sa.ForeignKey("tags.id"), primary_key=True)
