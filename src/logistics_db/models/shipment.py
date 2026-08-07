from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Shipment(Base):
    """One physical movement of packages from origin to destination, resulting from a booking."""
    __tablename__ = "shipments"

    shipment_id: Mapped[int] = mapped_column(primary_key=True)
    
    shipment_status: Mapped[str] = mapped_column(String(50), default="pending")

    estimated_delivery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    actual_delivery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Linking each shipment to its corresponding shipment booking
    booking_id: Mapped[int] = mapped_column(ForeignKey("shipment_bookings.booking_id"))
    # Linking each shipment to its origin facility
    origin_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.facility_id"), nullable=False)
    # Linking each shipment to its destination facility
    destination_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.facility_id"), nullable=False)