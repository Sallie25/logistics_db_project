"""added check constraints on status field

Revision ID: 04ec7c3850c1
Revises: a679f307284a
Create Date: 2026-08-08 06:12:57.344405

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '04ec7c3850c1'
down_revision: str | Sequence[str] | None = 'a679f307284a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "chk_booking_status",
        "shipment_bookings",
        "booking_status IN ('PENDING', 'CONFIRMED', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED')"
    )
    op.create_check_constraint(
        "chk_payment_status",
        "payments",
        "payment_status IN ('pending', 'settled', 'failed', 'refunded')"
    )
    op.create_check_constraint(
        "chk_shipment_status",
        "shipments",
        "shipment_status IN ('pending', 'in_transit', 'delivered', 'exception')"
    )
    op.create_check_constraint(
        "chk_leg_status",
        "transport_legs",
        "leg_status IN ('planned', 'dispatched', 'in_transit', 'arrived')"
    )
    op.create_check_constraint(
        "chk_driver_operational_status",
        "drivers",
        "operational_status IN ('active', 'inactive', 'terminated')"
    )
    op.create_check_constraint(
        "chk_vehicle_operational_status",
        "vehicles",
        "operational_status IN ('active', 'inactive', 'decomissioned')"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("chk_vehicle_operational_status", "vehicles", type_="check")
    op.drop_constraint("chk_driver_operational_status", "drivers", type_="check")
    op.drop_constraint("chk_leg_status", "transport_legs", type_="check")
    op.drop_constraint("chk_shipment_status", "shipments", type_="check")
    op.drop_constraint("chk_payment_status", "payments", type_="check")
    op.drop_constraint("chk_booking_status", "shipment_bookings", type_="check")
