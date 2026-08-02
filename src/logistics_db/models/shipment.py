from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Shipment(Base):
    """One physical movement of packages from origin to destination, resulting from a booking."""
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("shipment_bookings.id"))
    shipment_status: Mapped[str] = mapped_column(String(50), default = "pending")