from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from logistics_db.database import Base


class Package(Base):
    """A single physical parcel belonging to a Shipment."""
    __tablename__ = "packages"

    package_id: Mapped[int] = mapped_column(primary_key=True)
    
    package_code_epc: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    actual_weight_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    length_cm: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)

    width_cm: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)

    height_cm: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)

    customs_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    
    hazardous_materials_flag: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Connecting a package to the shipment it belongs to
    shipment_id: Mapped[int] = mapped_column(ForeignKey("shipments.shipment_id"), index=True, nullable=False)

    # Establishing a relationship with the Shipment model to facilitate easy access to shipment details from a package instance
    shipment: Mapped["Shipment"] = relationship("Shipment", back_populates="packages")

    # Establishing a relationship with the PackageFacilityTransit model to track the transit history of the package through various facilities
    facility_transits: Mapped[list["PackageFacilityTransit"]] = relationship(
        "PackageFacilityTransit", back_populates="package"
    )
