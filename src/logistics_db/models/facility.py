from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Facility(Base):
    """A warehouse or hub node in the logistics network."""
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    facility_name: Mapped[str] = mapped_column(String(150))
    facility_type: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    country_code: Mapped[str] = mapped_column(String(3))