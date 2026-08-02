from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Driver(Base):
    """Personnel who operate Vehicles across TransportLegs."""
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    home_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    license_type: Mapped[str] = mapped_column(String(50))