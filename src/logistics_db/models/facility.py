from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Facility(Base):
    """A warehouse or hub node in the logistics network."""
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    facility_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    facility_name: Mapped[str] = mapped_column(String(150), nullable=False)
    facility_type: Mapped[str] = mapped_column(String(100), nullable=False)
    address_line1: Mapped[str] = mapped_column(String(150), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    is_security_certified: Mapped[bool] = mapped_column(default=False, nullable=False)
    security_certification_level: Mapped[str | None] = mapped_column(String(20), nullable=True)