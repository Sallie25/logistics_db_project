from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class TransportLeg(Base):
    """
    Associative entity resolving Shipment <-> Vehicle/Driver (N:M).
    Each row is one discrete leg of a shipment's journey.
    """
    __tablename__ = "transport_legs"

    id: Mapped[int] = mapped_column(primary_key=True)
    shipment_id: Mapped[int] = mapped_column(ForeignKey("shipments.id"))
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"))
    leg_number: Mapped[int] = mapped_column(Integer, nullable=False)
    leg_status: Mapped[str] = mapped_column(String(50), nullable=False)

