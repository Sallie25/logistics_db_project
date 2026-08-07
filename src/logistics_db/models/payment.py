from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, func
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

    transaction_timestamp: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    # Linking each payment to its corresponding shipment booking and payer client
    booking_id: Mapped[int] = mapped_column(ForeignKey("shipment_bookings.booking_id"), unique=True)

    # Linking each payment to the client responsible for making the payment
    payer_client_id: Mapped[int] = mapped_column(ForeignKey("clients.client_id"), nullable=False)
