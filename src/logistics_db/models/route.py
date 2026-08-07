from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Route(Base):
    """Fixed, reusable transport corridor between two Facilities."""
    __tablename__ = "routes"

    route_id: Mapped[int] = mapped_column(primary_key=True)

    route_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    
  
    distance_km: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    standard_transit_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    transport_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Linking each route to its origin and destination facilities
    origin_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.facility_id"))

    # Linking each route to its destination facility
    destination_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.facility_id"))