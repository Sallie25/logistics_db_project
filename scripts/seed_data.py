"""
Seed script using factory_boy to generate realistic fake data,
respecting FK dependency order.
"""

import factory

from logistics_db.database import Session
from logistics_db.models import (
    Client,
    Driver,
    Facility,
    Package,
    Payment,
    Route,
    ServiceType,
    Shipment,
    ShipmentBooking,
    TransportLeg,
    Vehicle,
)


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"


# --- Client Factory ---

class ClientFactory(BaseFactory):
    class Meta:
        model = Client

    name = factory.Faker("company")
    primary_email = factory.Faker("email")
    phone_no = factory.Faker("phone_number")
    client_type = factory.Iterator(["COMMERCIAL_ACCOUNT", "RETAIL_GUEST"])
    billing_address_line1 = factory.Faker("street_address")
    billing_city = factory.Faker("city")
    billing_state = factory.Faker("state")
    billing_postal_code = factory.Faker("postcode")
    billing_country_code = factory.Faker("country_code")


# --- ServiceType and Facility Factories ---

class ServiceTypeFactory(BaseFactory):
    class Meta:
        model = ServiceType

    service_name = factory.Iterator(["Express", "Standard", "Economy"])
    max_delivery_hours = factory.Iterator([24, 72, 168])


class FacilityFactory(BaseFactory):
    class Meta:
        model = Facility

    facility_code = factory.Sequence(lambda n: f"FAC{n:03d}")
    facility_name = factory.Faker("company")
    facility_type = factory.Iterator(["GLOBAL_HUB", "REGIONAL_HUB", "SERVICE_CENTER"])
    address_line1 = factory.Faker("street_address")
    city = factory.Faker("city")
    country_code = factory.Faker("country_code")
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")
    is_security_certified = factory.Faker("boolean")
    security_certification_level = factory.Iterator(["LEVEL_1", "LEVEL_2", "LEVEL_3", None])


class ShipmentBookingFactory(BaseFactory):
    class Meta:
        model = ShipmentBooking

    booking_reference = factory.Sequence(lambda n: f"BK-{n:06d}")
    sender = factory.SubFactory(ClientFactory)
    receiver = factory.SubFactory(ClientFactory)
    payer = factory.SubFactory(ClientFactory)
    service_type = factory.SubFactory(ServiceTypeFactory)
    booking_status = factory.Iterator(["PENDING", "CONFIRMED", "IN_TRANSIT", "DELIVERED"])
    requires_pickup = factory.Faker("boolean")
    quoted_amount = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    quoted_currency_code = factory.Iterator(["USD", "NGN"])




# --- Entry point -----

def main():
    session = Session()


    # Clear existing data first, in reverse dependency order,
    # so re-running this script doesn't hit duplicate-key errors
    session.query(ShipmentBooking).delete()
    session.query(Facility).delete()
    session.query(ServiceType).delete()
    session.query(Client).delete()
    session.commit()

    ClientFactory._meta.sqlalchemy_session = session
    ServiceTypeFactory._meta.sqlalchemy_session = session
    FacilityFactory._meta.sqlalchemy_session = session
    ShipmentBookingFactory._meta.sqlalchemy_session = session

    clients = ClientFactory.create_batch(20)
    service_types = ServiceTypeFactory.create_batch(3)
    facilities = FacilityFactory.create_batch(10)
    session.commit()

    bookings = ShipmentBookingFactory.create_batch(15)
    session.commit()

    print(f"Created {len(clients)} clients")
    print(f"Created {len(service_types)} service types")
    print(f"Created {len(facilities)} facilities")
    print(f"Created {len(bookings)} shipment bookings")

    session.close()


if __name__ == "__main__":
    main()