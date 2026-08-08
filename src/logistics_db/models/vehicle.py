from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Vehicle(Base):
    """A fleet asset (van, truck, aircraft) used to move shipments."""
    __tablename__ = "vehicles"

    vehicle_id: Mapped[int] = mapped_column(primary_key=True)

    vin_or_tail_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=False)

    max_weight_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    max_volume_m3: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)

    operational_status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)


    """Foreign key relationships to other tables in the database"""
    
    # Linking each vehicle to its designated home facility
    home_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.facility_id"))


    """Check constraints to ensure data integrity and validity"""

    __table_args__ = (
                CheckConstraint(
                    "operational_status IN ('active','inactive','decomissioned')",
                    name="chk_vehicle_operational_status"
                ),
    )
