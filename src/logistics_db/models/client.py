from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from logistics_db.database import Base


class Client(Base):
    """
    People or organizations that send, receive shipments, or pay for shipments.
    """
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    primary_email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone_no: Mapped[str] = mapped_column(String(30), nullable=False)
    client_type: Mapped[str] = mapped_column(String(30), nullable=False)
    billing_address_line1: Mapped[str] = mapped_column(String(150), nullable=False)
    billing_city: Mapped[str] = mapped_column(String(100), nullable=False)
    billing_state: Mapped[str] = mapped_column(String(100), nullable=True)
    billing_postal_code: Mapped[str] = mapped_column(String(20), nullable=True)
    billing_country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)