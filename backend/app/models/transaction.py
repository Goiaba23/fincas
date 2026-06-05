import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class TransactionJournal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "transaction_journals"

    workspace_id = mapped_column(sa.Uuid, sa.ForeignKey("workspaces.id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    date = mapped_column(sa.Date, nullable=False)
    effective_date = mapped_column(sa.Date)
    currency_code: Mapped[str] = mapped_column(sa.String(3), sa.ForeignKey("currencies.code"))
    amount: Mapped[float] = mapped_column(sa.Numeric(15, 2), nullable=False)

    foreign_amount = mapped_column(sa.Numeric(15, 2))
    foreign_currency_id: Mapped[str | None] = mapped_column(sa.String(3), sa.ForeignKey("currencies.code"))
    exchange_rate = mapped_column(sa.Numeric(18, 8))

    payee_id = mapped_column(sa.Uuid, sa.ForeignKey("payees.id"))
    category_id = mapped_column(sa.Uuid, sa.ForeignKey("categories.id"))
    notes: Mapped[str | None] = mapped_column(sa.Text)

    is_installment: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    installment_number = mapped_column(sa.Integer)
    total_installments = mapped_column(sa.Integer)
    installment_total_amount = mapped_column(sa.Numeric(15, 2))

    recurring_id = mapped_column(sa.Uuid, sa.ForeignKey("recurring_transactions.id"))
    import_hash: Mapped[str | None] = mapped_column(sa.String(64))
    external_id: Mapped[str | None] = mapped_column(sa.String(255))

    sync_version: Mapped[int] = mapped_column(sa.Integer, default=1)
    is_pending: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    created_by = mapped_column(sa.Uuid, sa.ForeignKey("users.id"))

    workspace = sa.orm.relationship("Workspace")
    payee = sa.orm.relationship("Payee")
    category = sa.orm.relationship("Category")
    transactions = sa.orm.relationship("Transaction", back_populates="journal", cascade="all, delete-orphan")
    tags = sa.orm.relationship("Tag", secondary="journal_tag")


class Transaction(Base, UUIDMixin):
    __tablename__ = "transactions"

    journal_id = mapped_column(sa.Uuid, sa.ForeignKey("transaction_journals.id"), nullable=False)
    account_id = mapped_column(sa.Uuid, sa.ForeignKey("accounts.id"), nullable=False)
    amount: Mapped[float] = mapped_column(sa.Numeric(15, 2), nullable=False)
    is_reconciled: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    reconciled_at = mapped_column(sa.DateTime(timezone=True))
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0)

    journal = sa.orm.relationship("TransactionJournal", back_populates="transactions")
    account = sa.orm.relationship("Account")
