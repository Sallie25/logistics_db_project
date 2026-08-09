from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from logistics_db.database import Base


class ShipmentBooking(Base):
    """A table that represents a client's request to ship one or more packages."""
    __tablename__ = "shipment_bookings"

    booking_id: Mapped[int] = mapped_column(primary_key=True)

    booking_reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
   
    booking_status: Mapped[str] = mapped_column(String(50), default="pending")

    requires_pickup: Mapped[bool] = mapped_column(default=False, nullable=False)

    pickup_address_line1: Mapped[str | None] = mapped_column(String(150), nullable=True)

    pickup_city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    quoted_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    quoted_currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    """Foreign key relationships to other tables in the database"""

    # Linking each shipment booking to the client who is sending the shipment
    sender_client_id: Mapped[int] = mapped_column(ForeignKey("clients.client_id"),index=True, nullable=False)
    # Linking each shipment booking to the client who is receiving the shipment
    receiver_client_id: Mapped[int] = mapped_column(ForeignKey("clients.client_id"), index=True, nullable=False)
    # Linking each shipment booking to the client who is paying for the shipment
    payer_client_id: Mapped[int] = mapped_column(ForeignKey("clients.client_id"), index=True, nullable=False)
    # Linking each shipment booking to the service type selected for the shipment
    service_type_id: Mapped[int] = mapped_column(ForeignKey("service_types.service_type_id"), index=True, nullable=False)

    """Check constraints to ensure data integrity and validity"""

    __table_args__ = (
                    CheckConstraint(
                        "booking_status IN ('PENDING', 'CONFIRMED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED')",
                        name='chk_booking_status'
                    ),
    )

    # --- One to Many Relationships ---- Talks to the Client model for sender, receiver, and payer relationships

    receiver: Mapped["Client"] = relationship(foreign_keys=[receiver_client_id], back_populates="bookings_received")

    payer: Mapped["Client"] = relationship(foreign_keys=[payer_client_id], back_populates="bookings_paid")

    sender: Mapped["Client"] = relationship(foreign_keys=[sender_client_id], back_populates="bookings_sent") 
    
    service_type: Mapped["ServiceType"] = relationship(back_populates="bookings")

    # one to one relationship with Shipment model for shipment relationship
    shipments: Mapped["Shipment"] = relationship("Shipment", back_populates="booking", uselist=False)

    # one to one relationship with Payment model for payment relationship
    payment: Mapped["Payment"] = relationship("Payment", back_populates="booking", uselist=False)