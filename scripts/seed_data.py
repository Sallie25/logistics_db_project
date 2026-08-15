"""
Seed script using factory_boy to generate realistic fake data,
respecting FK dependency order.
"""

import random
from datetime import datetime, timedelta, timezone

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
from logistics_db.models.package_facility_transit import PackageFacilityTransit


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
    # Clients must exist before any booking references them as sender/receiver/payer.
    # Bookings are generated in the -6M..now window, so anchoring clients to
    # -18M..-6M guarantees created_at(client) < created_at(any booking that uses it).
    created_at = factory.Faker(
        "date_time_between", start_date="-18M", end_date="-6M", tzinfo=timezone.utc
    )


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
    pickup_address_line1 = factory.Maybe(
    "requires_pickup",
    yes_declaration=factory.Faker("street_address"),
    no_declaration=None,
    )
    pickup_city = factory.Maybe(
        "requires_pickup",
        yes_declaration=factory.Faker("city"),
        no_declaration=None,
    )
    created_at = factory.Faker(
        "date_time_between", start_date="-6M", end_date="now", tzinfo=timezone.utc
    )

class PaymentFactory(BaseFactory):
    class Meta:
        model = Payment

    booking = factory.SubFactory(ShipmentBookingFactory)
    payer = factory.SelfAttribute("booking.payer")
    amount = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    currency_code = factory.Iterator(["USD", "NGN"])
    payment_type = factory.Iterator(["BASE_FREIGHT", "CUSTOMS_DUTY", "WEIGHT_ADJUSTMENT"])
    payment_method = factory.Iterator(["CARD", "BANK_TRANSFER", "CORPORATE_ACCOUNT"])
    payment_status = factory.Iterator(["pending", "settled", "failed", "refunded"])
    payment_reference = factory.Sequence(lambda n: f"TXN-{n:08d}")
    # A payment can only happen after its booking was placed.
    transaction_timestamp = factory.LazyAttribute(
        lambda o: min(
            o.booking.created_at + timedelta(hours=random.randint(1, 72)),
            datetime.now(timezone.utc),
        )
    )


class RouteFactory(BaseFactory):
    class Meta:
        model = Route

    route_code = factory.Sequence(lambda n: f"RT-{n:04d}")
    origin_facility = factory.SubFactory(FacilityFactory)
    destination_facility = factory.SubFactory(FacilityFactory)
    distance_km = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    standard_transit_hours = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    transport_mode = factory.Iterator(["air", "road", "rail", "sea"])
    is_active = factory.Faker("boolean", chance_of_getting_true=90)


class VehicleFactory(BaseFactory):
    class Meta:
        model = Vehicle

    vin_or_tail_number = factory.Sequence(lambda n: f"VIN{n:08d}")
    home_facility = factory.SubFactory(FacilityFactory)
    vehicle_type = factory.Iterator(["DELIVERY_VAN", "LINEHAUL_TRUCK", "AIRCRAFT_FEEDER"])
    max_weight_kg = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    max_volume_m3 = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    operational_status = "active"


class DriverFactory(BaseFactory):
    class Meta:
        model = Driver

    employee_number = factory.Sequence(lambda n: f"EMP{n:05d}")
    home_facility = factory.SubFactory(FacilityFactory)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_no = factory.Faker("phone_number")
    license_type = factory.Iterator(["CLASS_A", "CLASS_B", "CLASS_C"])
    license_expiry_date = factory.Faker("future_date", end_date="+2y")
    operational_status = "active"


class ShipmentFactory(BaseFactory):
    class Meta:
        model = Shipment

    booking = factory.SubFactory(ShipmentBookingFactory)
    origin_facility = factory.SubFactory(FacilityFactory)
    destination_facility = factory.SubFactory(FacilityFactory)
    shipment_status = factory.Iterator(["pending", "in_transit", "delivered", "exception"])
    # A shipment is created shortly after its booking is placed, never before it.
    created_at = factory.LazyAttribute(
        lambda o: min(
            o.booking.created_at + timedelta(hours=random.randint(1, 48)),
            datetime.now(timezone.utc),
        )
    )
    # The estimate is made at shipment-creation time and points into the future
    # relative to that moment, so it's allowed to land after "now".
    estimated_delivery_date = factory.LazyAttribute(
        lambda o: o.created_at + timedelta(days=random.randint(1, 10))
    )
    actual_delivery_date = factory.Maybe(
        factory.LazyAttribute(lambda o: o.shipment_status == "delivered"),
        yes_declaration=factory.LazyAttribute(
            lambda o: min(
                o.created_at + timedelta(days=random.randint(1, 12)),
                datetime.now(timezone.utc),
            )
        ),
        no_declaration=None,
    )


class PackageFactory(BaseFactory):
    class Meta:
        model = Package

    shipment = factory.SubFactory(ShipmentFactory)
    package_code_epc = factory.Sequence(lambda n: f"EPC{n:010d}")
    actual_weight_kg = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    length_cm = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    width_cm = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    height_cm = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    hazardous_materials_flag = factory.Faker("boolean", chance_of_getting_true=10)
    customs_value = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)


class TransportLegFactory(BaseFactory):
    class Meta:
        model = TransportLeg

    shipment = factory.SubFactory(ShipmentFactory)
    route = factory.SubFactory(RouteFactory)
    vehicle = factory.SubFactory(VehicleFactory)
    driver = factory.SubFactory(DriverFactory)
    leg_number = factory.Sequence(lambda n: n + 1)
    leg_status = factory.Iterator(["planned", "dispatched", "in_transit", "arrived"])
    scheduled_departure = factory.Faker("future_datetime", end_date="+5d", tzinfo=timezone.utc)
    scheduled_arrival = factory.Faker("future_datetime", end_date="+10d", tzinfo=timezone.utc)
    actual_departure = factory.Maybe(
    factory.LazyAttribute(lambda o: o.leg_status in ["dispatched", "in_transit", "arrived"]),
    yes_declaration=factory.Faker("past_datetime", start_date="-10d", tzinfo=timezone.utc),
    no_declaration=None,
    )
    actual_arrival = factory.Maybe(
    factory.LazyAttribute(lambda o: o.leg_status == "arrived"),
    yes_declaration=factory.Faker("past_datetime", start_date="-5d", tzinfo=timezone.utc),
    no_declaration=None,
    )
    


class PackageFacilityTransitFactory(BaseFactory):
    class Meta:
        model = PackageFacilityTransit

    package = factory.SubFactory(PackageFactory)
    facility = factory.SubFactory(FacilityFactory)
    # A package can't be scanned into a facility before its shipment even exists.
    inbound_timestamp = factory.LazyAttribute(
        lambda o: min(
            o.package.shipment.created_at + timedelta(hours=random.randint(1, 96)),
            datetime.now(timezone.utc),
        )
    )
    sorting_lane = factory.Sequence(lambda n: f"LANE-{n % 20}")
    outbound_timestamp = factory.Maybe(
    factory.Faker("boolean", chance_of_getting_true=70),
    yes_declaration=factory.LazyAttribute(
        lambda o: o.inbound_timestamp + timedelta(hours=random.randint(1, 48))
    ),
    no_declaration=None,
    )




# --- Entry point -----

def main():
    session = Session()

    # Clear existing data first, in reverse dependency order
    session.query(PackageFacilityTransit).delete()
    session.query(TransportLeg).delete()
    session.query(Package).delete()
    session.query(Shipment).delete()
    session.query(Payment).delete()
    session.query(Vehicle).delete()
    session.query(Driver).delete()
    session.query(Route).delete()
    session.query(ShipmentBooking).delete()
    session.query(Facility).delete()
    session.query(ServiceType).delete()
    session.query(Client).delete()
    session.commit()

    # Bind every factory to this session
    for factory_cls in [
        ClientFactory, ServiceTypeFactory, FacilityFactory, ShipmentBookingFactory,
        PaymentFactory, RouteFactory, VehicleFactory, DriverFactory,
        ShipmentFactory, PackageFactory, TransportLegFactory, PackageFacilityTransitFactory,
    ]:
        factory_cls._meta.sqlalchemy_session = session

    # --- Step 1: create a small reusable POOL of parent records ---
    clients_pool = ClientFactory.create_batch(100)
    service_types_pool = ServiceTypeFactory.create_batch(3)
    facilities_pool = FacilityFactory.create_batch(20)
    session.commit()
    print(f"Created {len(clients_pool)} clients (pool)")
    print(f"Created {len(service_types_pool)} service types (pool)")
    print(f"Created {len(facilities_pool)} facilities (pool)")

    # --- Step 2: scale shipment_bookings to 10k+, reusing the pool ---
    bookings = ShipmentBookingFactory.create_batch(
        10000,
        sender=factory.LazyFunction(lambda: random.choice(clients_pool)),
        receiver=factory.LazyFunction(lambda: random.choice(clients_pool)),
        payer=factory.LazyFunction(lambda: random.choice(clients_pool)),
        service_type=factory.LazyFunction(lambda: random.choice(service_types_pool)),
    )
    session.commit()
    print(f"Created {len(bookings)} shipment bookings")

    # --- Step 3: payments, reusing bookings pool + clients pool ---
    payments = [PaymentFactory(booking=b, payer=b.payer) for b in bookings]
    session.commit()
    print(f"Created {len(payments)} payments")

    # --- Step 4: everything else, kept at smaller/original scale ---
    routes = RouteFactory.create_batch(
        8,
        origin_facility=factory.LazyFunction(lambda: random.choice(facilities_pool)),
        destination_facility=factory.LazyFunction(lambda: random.choice(facilities_pool)),
    )
    vehicles = VehicleFactory.create_batch(
        10, home_facility=factory.LazyFunction(lambda: random.choice(facilities_pool))
    )
    drivers = DriverFactory.create_batch(
        10, home_facility=factory.LazyFunction(lambda: random.choice(facilities_pool))
    )
    session.commit()
    print(f"Created {len(routes)} routes")
    print(f"Created {len(vehicles)} vehicles")
    print(f"Created {len(drivers)} drivers")

    shipments = ShipmentFactory.create_batch(
        15,
        booking=factory.LazyFunction(lambda: random.choice(bookings)),
        origin_facility=factory.LazyFunction(lambda: random.choice(facilities_pool)),
        destination_facility=factory.LazyFunction(lambda: random.choice(facilities_pool)),
    )
    session.commit()
    print(f"Created {len(shipments)} shipments")

    packages = PackageFactory.create_batch(
        30, shipment=factory.LazyFunction(lambda: random.choice(shipments))
    )
    session.commit()
    print(f"Created {len(packages)} packages")

    transport_legs = TransportLegFactory.create_batch(
        25,
        shipment=factory.LazyFunction(lambda: random.choice(shipments)),
        route=factory.LazyFunction(lambda: random.choice(routes)),
        vehicle=factory.LazyFunction(lambda: random.choice(vehicles)),
        driver=factory.LazyFunction(lambda: random.choice(drivers)),
    )
    session.commit()
    print(f"Created {len(transport_legs)} transport legs")

    transits = PackageFacilityTransitFactory.create_batch(
        40,
        package=factory.LazyFunction(lambda: random.choice(packages)),
        facility=factory.LazyFunction(lambda: random.choice(facilities_pool)),
    )
    session.commit()
    print(f"Created {len(transits)} package facility transits")

    session.close()


if __name__ == "__main__":
    main()