import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from social_media.models import Post
from social_media.tasks import moderate_post_content

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Post)
def trigger_post_moderation(sender, instance, created, update_fields=None, **_kwargs):
    """Trigger post moderation on creation or content updates, avoiding infinite loops."""  # noqa: E501
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
