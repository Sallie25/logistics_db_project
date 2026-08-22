import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from logistics_db.database import Base
from logistics_db.models import Client, Facility, ServiceType, ShipmentBooking


@pytest.fixture()
def session():
    """
    A fresh in-memory SQLite database per test. StaticPool keeps a single
    connection alive for the whole test (in-memory SQLite normally forgets
    everything the moment a connection closes), and every test gets its own
    engine, so tests can't leak state into each other.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    db_session = TestSession()
    yield db_session
    db_session.close()
    engine.dispose()


@pytest.fixture()
def facilities(session):
    """Two facilities, ready to use as origin/destination."""
    f1 = Facility(
        facility_code="F1", facility_name="Hub 1", facility_type="REGIONAL_HUB",
        address_line1="1 Hub Rd", city="Lagos", country_code="NG",
        latitude="6.5244", longitude="3.3792", is_security_certified=True,
    )
    f2 = Facility(
        facility_code="F2", facility_name="Hub 2", facility_type="REGIONAL_HUB",
        address_line1="2 Hub Rd", city="Abuja", country_code="NG",
        latitude="9.0765", longitude="7.3986", is_security_certified=False,
    )
    session.add_all([f1, f2])
    session.commit()
    return f1, f2


@pytest.fixture()
def booking(session):
    """A confirmed ShipmentBooking with its client/service_type parents already saved."""
    sender = Client(
        name="Acme", primary_email="acme@example.com", phone_no="555-0100",
        client_type="COMMERCIAL_ACCOUNT", billing_address_line1="1 Main St",
        billing_city="Lagos", billing_country_code="NG",
    )
    receiver = Client(
        name="Beta", primary_email="beta@example.com", phone_no="555-0101",
        client_type="COMMERCIAL_ACCOUNT", billing_address_line1="2 Main St",
        billing_city="Lagos", billing_country_code="NG",
    )
    service_type = ServiceType(service_name="Standard", max_delivery_hours=72)
    session.add_all([sender, receiver, service_type])
    session.commit()

    shipment_booking = ShipmentBooking(
        booking_reference="BK-TEST-0001",
        sender=sender, receiver=receiver, payer=sender, service_type=service_type,
        booking_status="CONFIRMED", requires_pickup=False,
        quoted_amount="150.00", quoted_currency_code="USD",
    )
    session.add(shipment_booking)
    session.commit()
    return shipment_booking
