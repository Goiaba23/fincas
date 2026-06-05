from pgvector.sqlalchemy import Vector
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class AIConnection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_connections"

    user_id = mapped_column(sa.Uuid, sa.ForeignKey("users.id"), nullable=False)
    provider: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    display_name: Mapped[str | None] = mapped_column(sa.String(100))
    model: Mapped[str | None] = mapped_column(sa.String(100))
    config = mapped_column(sa.JSON, default=dict)
    is_default: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)


class AIConversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_conversations"

    user_id = mapped_column(sa.Uuid, sa.ForeignKey("users.id"), nullable=False)
    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"))
    title: Mapped[str | None] = mapped_column(sa.String(255))
    provider_id = mapped_column(sa.Uuid, sa.ForeignKey("ai_connections.id"))

    messages = sa.orm.relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AIMessage.created_at")


class AIMessage(Base, UUIDMixin):
    __tablename__ = "ai_messages"

    conversation_id = mapped_column(sa.Uuid, sa.ForeignKey("ai_conversations.id"), nullable=False)
    role: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    tool_calls = mapped_column(sa.JSON)
    token_count = mapped_column(sa.Integer)
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))

    conversation = sa.orm.relationship("AIConversation", back_populates="messages")


class KnowledgeDocument(Base, UUIDMixin):
    __tablename__ = "knowledge_documents"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    title: Mapped[str | None] = mapped_column(sa.String(255))
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    content_type: Mapped[str] = mapped_column(sa.String(50), default="text")
    # pgvector embedding (1536 dimensions for OpenAI/text-embedding-3-small)
    embedding = mapped_column(Vector(1536))
    metadata_ = mapped_column("metadata", sa.JSON, default=dict)
    created_by = mapped_column(sa.Uuid, sa.ForeignKey("users.id"))
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))
