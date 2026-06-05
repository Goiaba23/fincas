import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SyncMessage(Base):
    __tablename__ = "sync_messages"

    id = mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)
    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    user_id = mapped_column(sa.Uuid, sa.ForeignKey("users.id"), nullable=False)
    dataset: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    row_id = mapped_column(sa.Uuid, nullable=False)
    column_name: Mapped[str | None] = mapped_column(sa.String(100))
    value = mapped_column(sa.JSON)
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    vector_clock: Mapped[str | None] = mapped_column(sa.Text)
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))
