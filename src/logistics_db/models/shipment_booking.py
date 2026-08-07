from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class ShipmentBooking(Base):
    """A table that represents a client's request to ship one or more packages."""
    __tablename__ = "shipment_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    sender_client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    receiver_client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    payer_client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    service_type_id: Mapped[int] = mapped_column(ForeignKey("service_types.id"), nullable=False)
    booking_status: Mapped[str] = mapped_column(String(50), default="pending")
    requires_pickup: Mapped[bool] = mapped_column(default=False, nullable=False)
    pickup_address_line1: Mapped[str | None] = mapped_column(String(150), nullable=True)
    pickup_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quoted_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quoted_currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)