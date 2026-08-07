from datetime import datetime

from sqlalchemy import ForeignKey, String,DateTime
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class PackageFacilityTransit(Base):
    """
    Associative entity resolving Package <-> Facility (N:M).
    Each row records one package's dwell time inside one facility.
    """
    __tablename__ = "package_facility_transits"

    transit_id: Mapped[int] = mapped_column(primary_key=True)

    inbound_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)

    outbound_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),nullable=True)

    sorting_lane: Mapped[str] = mapped_column(String(50), nullable=False)

    # Connecting a package to the exact facility where it was scanned or processed
    package_id: Mapped[int] = mapped_column(ForeignKey("packages.package_id"))
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.facility_id"))
    
