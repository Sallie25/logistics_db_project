from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Payment(Base):
    """Financial transaction tied to exactly one ShipmentBooking (1:1)."""
    __tablename__ = "payments"

    payment_id: Mapped[int] = mapped_column(primary_key=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)

    payment_type: Mapped[str] = mapped_column(String(30), nullable=False)

    payment_method: Mapped[str] = mapped_column(String(30), nullable=True)

    payment_reference: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)

    payment_status: Mapped[str] = mapped_column(String(30), default="pending")

    transaction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(), nullable=False)

    """Foreign key relationships to other tables in the database"""

    # Linking each payment to its corresponding shipment booking and payer client
    booking_id: Mapped[int] = mapped_column(ForeignKey("shipment_bookings.booking_id"), unique=True)

    # Linking each payment to the client responsible for making the payment
    payer_client_id: Mapped[int] = mapped_column(ForeignKey("clients.client_id"), nullable=False)


    """Check constraints to ensure data integrity and validity"""

    __table_args__ = (
                    CheckConstraint(
                        "payment_status IN ('pending', 'settled', 'failed','refunded')",
                        name="chk_payment_status"
                        ),
    )