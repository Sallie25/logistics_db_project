from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Driver(Base):
    """Personnel who operate Vehicles across TransportLegs."""
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    home_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_no: Mapped[str] = mapped_column(String(30), nullable=False)
    license_type: Mapped[str] = mapped_column(String(50), nullable=False)
    license_expiry_date: Mapped[date] = mapped_column(nullable=False)
    operational_status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)