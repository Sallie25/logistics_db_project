from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    package_id: Mapped[int] = mapped_column(ForeignKey("packages.package_id"), index=True, nullable=False)
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.facility_id"), index=True, nullable=False)
    
    # one-to-many relationship with Package model for package relationship with facility transits
    package: Mapped["Package"] = relationship("Package", back_populates="facility_transits")

    # one-to-many relationship with Facility model for facility relationship with package transits
    facility: Mapped["Facility"] = relationship("Facility", back_populates="package_transits")