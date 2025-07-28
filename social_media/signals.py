import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from social_media.models import Post
from social_media.tasks import moderate_post_content

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Post)
def trigger_post_moderation(sender, instance, created, update_fields=None, **_kwargs):
    """
    Handles post moderation triggering logic upon creation or content updates.
    This function is intended to be used as a signal handler for post save events.
    It triggers asynchronous moderation for new posts and for posts whose content has changed,
    while avoiding infinite moderation loops by skipping updates originating from the moderation task itself.
    Args:
        sender: The model class sending the signal.
        instance: The instance of the post being saved.
        created (bool): Whether the instance was created (True) or updated (False).
        update_fields (Optional[set]): The set of fields updated during save, if any.
        **_kwargs: Additional keyword arguments.
    Returns:
        None
    """  # noqa: E501

    # Trigger moderation on post creation
    if created:
        logger.debug("Triggering moderation for new post %s", instance.id)
        transaction.on_commit(lambda: moderate_post_content.delay(instance.id))
        return

    # Skip moderation if this save is from the moderation task itself
    if update_fields and "is_potentially_harmful" in update_fields:
        logger.debug(
            "Skipping moderation for post %s - update from moderation task",
            instance.id,
        )
        return

    # Trigger moderation for post updates (content changes)
    if instance and instance.content and instance.content.strip():
        logger.debug("Post %s content updated, triggering moderation", instance.id)
        transaction.on_commit(lambda: moderate_post_content.delay(instance.id))
