from celery import shared_task

from core.users.models import User
from social_media.models import Post


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
