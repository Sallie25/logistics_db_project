from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class ShipmentBooking(Base):
    """
    A table that represents a client requests to ship one or more packages
    """

    __tablename__ = "shipment_bookings"

    id: Mapped[int] = mapped_column(primary_key = True)
    sender_client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    receiver_client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    payer_client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    booking_status: Mapped[str] = mapped_column(String(50)) 



