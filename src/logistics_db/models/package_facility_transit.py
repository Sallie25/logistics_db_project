from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class PackageFacilityTransit(Base):
    """
    Associative entity resolving Package <-> Facility (N:M).
    Each row records one package's dwell time inside one facility.
    """
    __tablename__ = "package_facility_transits"

    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("packages.id"))
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    inbound_timestamp: Mapped[datetime] = mapped_column(nullable=False)
    outbound_timestamp: Mapped[datetime] = mapped_column(nullable=True)
    sorting_lane: Mapped[str] = mapped_column(String(50), nullable=False)
    
