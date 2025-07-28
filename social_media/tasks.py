import logging

from celery import shared_task

from core.users.models import User
from social_media.models import Post
from social_media.utils.moderation import ContentModerator

logger = logging.getLogger(__name__)


@shared_task
def create_post_log_view(post_id: str, user_id: str):
    """
    Creates a log view for a given post by a specific user.
    Args:
        post_id (str): The ID of the post to create a log view for.
        user_id (str): The ID of the user who is viewing the post.
    Returns:
        LogView: The created log view object for the post and user.
    Raises:
        Post.DoesNotExist: If no post with the given ID exists.
        User.DoesNotExist: If no user with the given ID exists.
    """

    post = Post.objects.get(id=post_id)
    user = User.objects.get(id=user_id)

    return post.create_log_view(user)


@shared_task(bind=True, autoretry_for=(Exception,), max_retries=5, retry_backoff=True)
def moderate_post_content(self, post_id: int):
    """
    Moderate post content for potentially harmful material.
    This method retrieves a post by ID and uses a ContentModerator to analyze
    the post content for potentially harmful material. Updates the post's
    moderation status accordingly.
    Args:
        post_id (int): The ID of the post to moderate.
    Returns:
        dict or bool: Returns a dictionary with 'skipped' and 'reason' keys if
                     content is empty, otherwise returns boolean indicating if
                     content is harmful (True) or safe (False).
    Raises:
        Exception: Re-raises any exception that occurs during post retrieval
                  after logging the error.
    Note:
        - Skips moderation for posts with empty or whitespace-only content
        - Updates the post's 'is_potentially_harmful' and 'updated_at' fields
        - Logs the moderation results for monitoring purposes
    """

    try:
        post = Post.objects.get(id=post_id)
    except Exception:
        logger.exception("Error moderating post %s", post_id)
        raise

    if not post.content.strip():
        logger.info("Skipping moderation for empty post content: %s", post_id)
        return {"skipped": True, "reason": "Empty content"}

    moderator = ContentModerator()
    is_harmful = moderator.is_potentially_harmful(post.content)

    if is_harmful:
        logger.info("Post %s flagged as potentially harmful", post_id)
        post.is_potentially_harmful = True
    else:
        logger.info("Post %s is safe", post_id)
        post.is_potentially_harmful = False

    post.save(update_fields=["is_potentially_harmful", "updated_at"])
    return is_harmful
