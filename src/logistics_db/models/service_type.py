from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class ServiceType(Base):
    """Carrier product/service tier offering (e.g., Express, Standard)."""
    __tablename__ = "service_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_delivery_hours: Mapped[int | None] = mapped_column(nullable=True)