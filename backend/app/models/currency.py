import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Currency(Base):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(sa.String(3), primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(sa.String(10), nullable=False)
    decimal_places: Mapped[int] = mapped_column(sa.Integer, default=2)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)


class ExchangeRate(Base, UUIDMixin):
    __tablename__ = "exchange_rates"

    from_currency: Mapped[str] = mapped_column(sa.String(3), sa.ForeignKey("currencies.code"), nullable=False)
    to_currency: Mapped[str] = mapped_column(sa.String(3), sa.ForeignKey("currencies.code"), nullable=False)
    rate: Mapped[float] = mapped_column(sa.Numeric(18, 8), nullable=False)
    date = mapped_column(sa.Date, nullable=False)
    source: Mapped[str] = mapped_column(sa.String(50), default="bcb_ptax")

    __table_args__ = (sa.UniqueConstraint("from_currency", "to_currency", "date"),)
