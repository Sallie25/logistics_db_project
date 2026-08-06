from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Shipment(Base):
    """One physical movement of packages from origin to destination, resulting from a booking."""
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("shipment_bookings.id"))
    destination_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"), nullable=False)
    shipment_status: Mapped[str] = mapped_column(String(50), default="pending")
    estimated_delivery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_delivery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)