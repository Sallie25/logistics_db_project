from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from logistics_db.database import Base


class Shipment(Base):
    """One physical movement of packages from origin to destination, resulting from a booking."""
    __tablename__ = "shipments"

    shipment_id: Mapped[int] = mapped_column(primary_key=True)
    
    shipment_status: Mapped[str] = mapped_column(String(50), default="pending")

    estimated_delivery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    actual_delivery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    """Foreign key relationships to other tables in the database"""

    # Linking each shipment to its corresponding shipment booking
    booking_id: Mapped[int] = mapped_column(ForeignKey("shipment_bookings.booking_id"), index = True, nullable = False)
    # Linking each shipment to its origin facility
    origin_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.facility_id"), index = True, nullable=False)
    # Linking each shipment to its destination facility
    destination_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.facility_id"), index = True, nullable=False)


    """Check constraints to ensure data integrity and validity"""
    
    __table_args__ = (
            CheckConstraint(
                "shipment_status IN ('pending', 'in_transit', 'delivered','exception')",
                name='chk_shipment_status'
            ),
    )

    # one-to-one relationship with ShipmentBooking model for booking relationship
    booking: Mapped["ShipmentBooking"] = relationship("ShipmentBooking", back_populates="shipments")

    # one-to-many relationship with Facility model for origin
    origin_facility: Mapped["Facility"] = relationship(
        "Facility", foreign_keys=[origin_facility_id], back_populates="shipments_originating"
    )

    # one-to-many relationship with Facility model for destination
    destination_facility: Mapped["Facility"] = relationship(
        "Facility", foreign_keys=[destination_facility_id], back_populates="shipments_terminating"
    )
    # many-to-one relationship with Package model for packages relationship
    packages: Mapped[list["Package"]] = relationship("Package", back_populates="shipment")

    # many-to-one relationship with TransportLeg model for transport legs relationship
    transport_legs: Mapped[list["TransportLeg"]] = relationship("TransportLeg", back_populates="shipment")