import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from vendors.models import Vendor
from vendors.tasks import send_vendor_discord_notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Vendor)
def trigger_vendor_notification(
    sender,
    instance,
    created,
    update_fields=None,
    **_kwargs,
):
    """
    Handles vendor notification triggering logic for creation and updates.

    This function monitors vendor lifecycle events and sends appropriate
    Discord webhook notifications:
    - New vendor registration (creation)
    - Review status changes (approval, rejection, resubmission)

    The notification is sent asynchronously using Celery to avoid blocking
    the request and uses transaction.on_commit() to ensure DB consistency.

    Uses django-simple-history to detect status changes by comparing current
    instance with the most recent historical record.

    Args:
        sender: The model class sending the signal (Vendor).
        instance: The instance of the vendor being saved.
        created (bool): Whether the instance was created (True) or updated (False).
        update_fields (Optional[set]): The set of fields updated during save, if any.
        **_kwargs: Additional keyword arguments.

    Returns:
        None
    """
    # Trigger notification on vendor creation
    if created:
        logger.debug("Triggering notification for new vendor %s", instance.id)
        transaction.on_commit(
            lambda: send_vendor_discord_notification.delay(instance.id, "created"),
        )
        return

    # On updates, check if review_status changed
    # If update_fields is None, all fields may have changed
    # If update_fields is set and contains 'review_status', status changed
    if update_fields is None or "review_status" in update_fields:
        try:
            # Use django-simple-history to get the previous state
            # history.all()[0] is the current state (just saved by simple-history)
            # history.all()[1] is the previous state (what we need)
            history_records = list(instance.history.all()[:2])

            if len(history_records) >= 2:  # noqa: PLR2004
                previous_instance = history_records[1]
                if previous_instance.review_status != instance.review_status:
                    old_status = previous_instance.review_status
                    logger.debug(
                        "Review status changed for vendor %s: %s -> %s",
                        instance.id,
                        old_status,
                        instance.review_status,
                    )
                    # Capture old_status in lambda closure
                    transaction.on_commit(
                        lambda old=old_status: send_vendor_discord_notification.delay(
                            instance.id,
                            "status_changed",
                            old,
                        ),
                    )
            else:
                logger.debug(
                    "Insufficient history records for vendor %s, skipping status change notification",  # noqa: E501
                    instance.id,
                )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "Failed to check vendor %s status change history: %s",
                instance.id,
                e,
                exc_info=True,
            )
