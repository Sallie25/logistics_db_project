from datetime import date

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Driver(Base):
    """Personnel who operate Vehicles across TransportLegs."""
    __tablename__ = "drivers"

    driver_id: Mapped[int] = mapped_column(primary_key=True)

    employee_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
 
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)

    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    phone_no: Mapped[str] = mapped_column(String(30), nullable=False)

    license_type: Mapped[str] = mapped_column(String(50), nullable=False)

    license_expiry_date: Mapped[date] = mapped_column(nullable=False)

    operational_status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)


    """Foreign key relationships to other tables in the database"""

    # Connecting a driver to their home facility (where they are based or where they report to)
    home_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.facility_id"))


    """Check constraints to ensure data integrity and validity"""

    __table_args__ = (
                CheckConstraint(
                    "operational_status IN ('active','inactive','terminated')",
                    name="chk_driver_operational_status"
                ),
    )
