from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from logistics_db.database import Base


class ExchangeRates(Base):
    """Exchange rates for different currencies, quoted against NGN."""
    __tablename__ = "exchange_rates"

    currency_code: Mapped[str] = mapped_column(String(3), primary_key=True)

    rate_to_ngn: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # --- One to Many Relationship --- one currency can back many payments
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="currency"
    )

    