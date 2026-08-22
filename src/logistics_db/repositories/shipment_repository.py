import logging

from sqlalchemy.exc import IntegrityError

from logistics_db.database import Session
from logistics_db.models import Shipment

logger = logging.getLogger(__name__)


class ShipmentRepository:
    def __init__(self, session):
        self.session = session

    def create_shipment(self, **kwargs):
        """
        Create a new Shipment. Commits on success; rolls back and re-raises
        on any database integrity error (e.g., a constraint violation).
        """
        shipment = Shipment(**kwargs)
        self.session.add(shipment)
        logger.info("Transaction started: creating shipment (%r)", kwargs)
        try:
            self.session.commit()
        except IntegrityError:
            logger.exception("Failed to create shipment: %r", kwargs)
            self.session.rollback()
            logger.warning("Transaction rolled back: create_shipment(%r)", kwargs)
            raise
        logger.info("Transaction succeeded: created shipment %s", shipment.shipment_id)
        return shipment

    def get_shipment(self, shipment_id):
        """
        Look up a single Shipment by its primary key. Returns the Shipment
        instance if found, or None if no shipment with that ID exists.
        """
        return self.session.get(Shipment, shipment_id)

    def update_shipment_status(self, shipment_id, new_status):
        """
        Update the shipment_status of an existing Shipment. Returns the
        updated Shipment on success, or None if no shipment with that ID
        exists. Commits on success; rolls back and re-raises on any database
        integrity error (e.g., an invalid status value).
        """
        shipment = self.session.get(Shipment, shipment_id)
        if shipment is None:
            return None

        shipment.shipment_status = new_status
        logger.info(
            "Transaction started: updating shipment %s to status %r",
            shipment_id, new_status,
        )
        try:
            self.session.commit()
        except IntegrityError:
            logger.exception(
                "Failed to update shipment %s to status %r", shipment_id, new_status
            )
            self.session.rollback()
            logger.warning(
                "Transaction rolled back: update_shipment_status(%s, %r)",
                shipment_id, new_status,
            )
            raise
        logger.info("Transaction succeeded: shipment %s is now %r", shipment_id, new_status)
        return shipment

    def delete_shipment(self, shipment_id):
        """
        Delete a Shipment by its primary key. Returns True if a shipment was
        found and deleted, or False if no shipment with that ID exists.
        Commits on success; rolls back and re-raises on any database
        integrity error (e.g., the shipment still has packages or transport
        legs referencing it).
        """
        shipment = self.session.get(Shipment, shipment_id)
        if shipment is None:
            return False

        self.session.delete(shipment)
        logger.info("Transaction started: deleting shipment %s", shipment_id)
        try:
            self.session.commit()
        except IntegrityError:
            logger.exception(
                "Failed to delete shipment %s — it may still have dependent "
                "packages or transport legs", shipment_id
            )
            self.session.rollback()
            logger.warning("Transaction rolled back: delete_shipment(%s)", shipment_id)
            raise
        logger.info("Transaction succeeded: deleted shipment %s", shipment_id)
        return True