from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Route(Base):
    """Fixed, reusable transport corridor between two Facilities."""
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    origin_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    destination_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    distance_km: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    transport_mode: Mapped[str] = mapped_column(String(50), nullable=False)