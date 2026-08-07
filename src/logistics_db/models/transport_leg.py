from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class TransportLeg(Base):
    """
    Associative entity resolving Shipment to Vehicle/Driver (N:M) - Many to Many relationship.
    Each row is one discrete leg of a shipment's journey.
    """
    __tablename__ = "transport_legs"

    leg_id: Mapped[int] = mapped_column(primary_key=True)
   
    leg_number: Mapped[int] = mapped_column(Integer, nullable=False)

    leg_status: Mapped[str] = mapped_column(String(50), nullable=False)

    scheduled_departure: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    actual_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    scheduled_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


    # Connecting each transport leg to the shipment it is moving
    shipment_id: Mapped[int] = mapped_column(ForeignKey("shipments.shipment_id"))

    # Connecting each transport leg to the planned route it follows
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.route_id"))

    # Assigning the vehicle responsible for this transport leg
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.vehicle_id"))

    # Assigning the driver responsible for operating the vehicle during this transport leg
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.driver_id"))