import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from social_media.models import Post
from social_media.tasks import moderate_post_content

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Post)
def trigger_post_moderation(_sender, instance, created, **_kwargs):
    # Trigger moderation on post creation
    if created:
        logger.debug("Triggering moderation for new post %s", instance.id)
        transaction.on_commit(lambda: moderate_post_content.delay(instance.id))
        return

    # For updates, compare current content with database value
    try:
        old_post = Post.objects.get(pk=instance.pk)
        if old_post.content.strip() != instance.content.strip():
            logger.debug(
                "Triggering moderation for content change in post %s",
                instance.id,
            )
            transaction.on_commit(lambda: moderate_post_content.delay(instance.id))
    except Post.DoesNotExist:
        # This shouldn't happen for updates, but handle gracefully
        logger.warning(
            "Post %s not found in database during update signal",
            instance.id,
        )
