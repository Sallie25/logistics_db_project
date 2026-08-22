import pytest
from sqlalchemy.exc import IntegrityError

from logistics_db.models import Package
from logistics_db.repositories.shipment_repository import ShipmentRepository

# --- create_shipment ---------------------------------------------------

def test_create_shipment_success(session, booking, facilities):
    origin, destination = facilities
    repo = ShipmentRepository(session)

    shipment = repo.create_shipment(
        booking=booking, origin_facility=origin, destination_facility=destination,
        shipment_status="pending",
    )

    assert shipment.shipment_id is not None
    assert shipment.shipment_status == "pending"


def test_create_shipment_invalid_status_rolls_back(session, booking, facilities):
    origin, destination = facilities
    repo = ShipmentRepository(session)

    with pytest.raises(IntegrityError):
        repo.create_shipment(
            booking=booking, origin_facility=origin, destination_facility=destination,
            shipment_status="NOT_A_REAL_STATUS",
        )

    # session must still be usable after the rollback
    assert session.query(Package).count() == 0


# --- get_shipment --------------------------------------------------------

def test_get_shipment_found(session, booking, facilities):
    origin, destination = facilities
    repo = ShipmentRepository(session)
    created = repo.create_shipment(
        booking=booking, origin_facility=origin, destination_facility=destination,
        shipment_status="pending",
    )

    found = repo.get_shipment(created.shipment_id)

    assert found is not None
    assert found.shipment_id == created.shipment_id


def test_get_shipment_not_found(session):
    repo = ShipmentRepository(session)
    assert repo.get_shipment(9999) is None


# --- update_shipment_status ----------------------------------------------

def test_update_shipment_status_success(session, booking, facilities):
    origin, destination = facilities
    repo = ShipmentRepository(session)
    created = repo.create_shipment(
        booking=booking, origin_facility=origin, destination_facility=destination,
        shipment_status="pending",
    )

    updated = repo.update_shipment_status(created.shipment_id, "in_transit")

    assert updated.shipment_status == "in_transit"


def test_update_shipment_status_not_found(session):
    repo = ShipmentRepository(session)
    assert repo.update_shipment_status(9999, "in_transit") is None


def test_update_shipment_status_invalid_rolls_back(session, booking, facilities):
    origin, destination = facilities
    repo = ShipmentRepository(session)
    created = repo.create_shipment(
        booking=booking, origin_facility=origin, destination_facility=destination,
        shipment_status="pending",
    )

    with pytest.raises(IntegrityError):
        repo.update_shipment_status(created.shipment_id, "NOT_A_REAL_STATUS")

    # the bad value must not have stuck — refetch from the DB to be sure
    reloaded = repo.get_shipment(created.shipment_id)
    assert reloaded.shipment_status == "pending"


# --- delete_shipment -------------------------------------------------------

def test_delete_shipment_success(session, booking, facilities):
    origin, destination = facilities
    repo = ShipmentRepository(session)
    created = repo.create_shipment(
        booking=booking, origin_facility=origin, destination_facility=destination,
        shipment_status="pending",
    )

    result = repo.delete_shipment(created.shipment_id)

    assert result is True
    assert repo.get_shipment(created.shipment_id) is None


def test_delete_shipment_not_found(session):
    repo = ShipmentRepository(session)
    assert repo.delete_shipment(9999) is False


def test_delete_shipment_blocked_by_dependent_package_rolls_back(session, booking, facilities):
    origin, destination = facilities
    repo = ShipmentRepository(session)
    created = repo.create_shipment(
        booking=booking, origin_facility=origin, destination_facility=destination,
        shipment_status="pending",
    )
    # A package still points at this shipment — the FK constraint should
    # block the delete rather than silently orphaning the package.
    session.add(Package(
        package_code_epc="EPC-TEST-0001", actual_weight_kg="1.00",
        length_cm="10.00", width_cm="10.00", height_cm="10.00",
        shipment=created,
    ))
    session.commit()

    with pytest.raises(IntegrityError):
        repo.delete_shipment(created.shipment_id)

    # shipment must still exist after the rollback
    assert repo.get_shipment(created.shipment_id) is not None
