import sqlalchemy as sa
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class MerchantMapping(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "merchant_mappings"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    merchant_name: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    normalized_name: Mapped[str] = mapped_column(sa.String(500), nullable=False, index=True)
    category_id = mapped_column(sa.Uuid, sa.ForeignKey("categories.id"))
    payee_id = mapped_column(sa.Uuid, sa.ForeignKey("payees.id"))
    is_income: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    is_recurring: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    confidence: Mapped[float] = mapped_column(sa.Float, default=1.0)


class CsvImportLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "csv_import_logs"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    account_id = mapped_column(sa.Uuid, sa.ForeignKey("accounts.id"))
    filename: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(20), default="pending")
    total_rows: Mapped[int] = mapped_column(sa.Integer, default=0)
    imported_rows: Mapped[int] = mapped_column(sa.Integer, default=0)
    skipped_rows: Mapped[int] = mapped_column(sa.Integer, default=0)
    error_rows: Mapped[int] = mapped_column(sa.Integer, default=0)
    errors: Mapped[str | None] = mapped_column(sa.Text)
