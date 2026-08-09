from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from logistics_db.database import Base


class Facility(Base):
    """A warehouse or hub node in the logistics network."""
    __tablename__ = "facilities"

    facility_id: Mapped[int] = mapped_column(primary_key=True)

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

    # many to one relationship with Driver, Vehicle, Route, Shipment, and PackageFacilityTransit models for various relationships
    drivers: Mapped[list["Driver"]] = relationship("Driver", back_populates="home_facility")

    # many to one relationship with Vehicle model for home facility relationship
    vehicles: Mapped[list["Vehicle"]] = relationship("Vehicle", back_populates="home_facility")
    
    # many to one relationship with Route model for origin facility relationship
    routes_originating: Mapped[list["Route"]] = relationship(
        "Route", foreign_keys="Route.origin_facility_id", back_populates="origin_facility"
    )
    # many to one relationship with Route model for destination facility relationship
    routes_terminating: Mapped[list["Route"]] = relationship(
        "Route", foreign_keys="Route.destination_facility_id", back_populates="destination_facility"
    )
    # many to one relationship with Shipment model for origin facility relationship
    shipments_originating: Mapped[list["Shipment"]] = relationship(
        "Shipment", foreign_keys="Shipment.origin_facility_id", back_populates="origin_facility"
    )
    # many to one relationship with Shipment model for destination facility relationship
    shipments_terminating: Mapped[list["Shipment"]] = relationship(
        "Shipment", foreign_keys="Shipment.destination_facility_id", back_populates="destination_facility"
    )
    # many to one relationship with PackageFacilityTransit model for facility relationship
    package_transits: Mapped[list["PackageFacilityTransit"]] = relationship(
        "PackageFacilityTransit", back_populates="facility"
    )