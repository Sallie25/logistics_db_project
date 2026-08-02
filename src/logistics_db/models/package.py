from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Package(Base):
    """A single physical parcel belonging to a Shipment."""
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(primary_key=True)
    shipment_id: Mapped[int] = mapped_column(ForeignKey("shipments.id"))
    actual_weight_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    customs_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)