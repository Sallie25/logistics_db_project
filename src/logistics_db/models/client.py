from logistics_db.database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Client(Base):
    """
    People or organizations that send, receive shipments or pay for shipments
    """
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    phone_no: Mapped[str] = mapped_column(String(30))
