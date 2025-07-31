from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.crypto import get_random_string

from core.users.models import User


class PostQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        """
        Filter posts based on privacy settings and user relationships
        """
        if not user or not user.is_authenticated:
            # Anonymous users can only see public posts
            return self.filter(privacy=Post.PUBLIC)

        # Authenticated users can see:
        # 1. All public posts
        # 2. Their own posts (regardless of privacy)
        # 3. Friends' posts where privacy is 'friends'

        # Get user's profile for friendship checks
        try:
            user_profile = user.profile
        except AttributeError:
            # User has no profile, can only see public posts
            return self.filter(privacy=Post.PUBLIC)

        # Get IDs of users who are friends (mutual followers)
        friend_profiles = user_profile.following.filter(
            following__followers__follower=user_profile,
        ).values_list("following_id", flat=True)

        friend_user_ids = []
        if friend_profiles:
            from accounts.models import Profile

            friend_user_ids = Profile.objects.filter(
                id__in=friend_profiles,
            ).values_list("user_id", flat=True)

        return self.filter(
            Q(privacy=Post.PUBLIC)  # Public posts
            | Q(user=user)  # Own posts
            | Q(privacy=Post.FRIENDS, user_id__in=friend_user_ids),  # Friends' posts
        )


class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)

    def visible_to_user(self, user):
        return self.get_queryset().visible_to_user(user)


class Post(models.Model):
    PUBLIC = "public"
    FRIENDS = "friends"
    ONLY_ME = "only_me"

    PRIVACY_CHOICES = [
        (PUBLIC, "Public"),
        (FRIENDS, "Friends"),
        (ONLY_ME, "Only Me"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=15, unique=True)
    content = models.TextField(default="")
    privacy = models.CharField(
        max_length=10,
        choices=PRIVACY_CHOICES,
        default=PUBLIC,
        help_text="Privacy setting for the post",
    )

    shared_count = models.PositiveIntegerField(default=0)

    is_potentially_harmful = models.BooleanField(
        default=False,
        help_text="Indicates if the post has been flagged as potentially harmful.",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.slug} — {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.slug:
            while True:
                new_slug = get_random_string(length=10)
                if not Post.objects.filter(slug=new_slug).exists():
                    self.slug = new_slug
                    break
        super().save(*args, **kwargs)

    def create_log_view(self, user):
        _, created = PostView.objects.get_or_create(post=self, user=user)
        return created

    def create_log_view_background(self, user):
        from social_media.tasks import create_post_log_view

        create_post_log_view.delay(self.id, user.id)


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="post_images/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Post {self.post.id}"

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super().delete(*args, **kwargs)


class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.parent:
            return f"Reply by {self.user.username} on Comment {self.parent.id}"
        return f"Comment by {self.user.username} on Post {self.post.id}"

    def clean(self):
        if self.parent and self.parent.post != self.post:
            msg = "Replies should be in the same post as the parent comment."
            raise ValidationError(
                msg,
            )


class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_post_view"),
        ]

    def __str__(self):
        return f"View by {self.user.username} on Post {self.post.id}"


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_post_like"),
        ]

    def __str__(self):
        return f"User {self.user.username} liked Post {self.post.id}"


class PostCommentLike(models.Model):
    """
    Model representing a user's like on a post comment.

    This model tracks when users like comments on posts, supporting social engagement
    features for the commenting system. Each user can only like a comment once,
    enforced by a unique constraint.

    Attributes:
        comment (ForeignKey): The comment being liked
        user (ForeignKey): The user who liked the comment
        created_at (DateTimeField): Timestamp when the like was created

    Constraints:
        - Unique constraint on (comment, user) to prevent duplicate likes
        - Cascade delete when comment or user is deleted

    Example:
        # Create a like on a comment
        like = PostCommentLike.objects.create(comment=comment, user=user)

        # Check if user liked a comment
        liked = PostCommentLike.objects.filter(comment=comment, user=user).exists()
    """

    comment = models.ForeignKey(
        PostComment,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["comment", "user"],
                name="unique_comment_like",
            ),
        ]

    def __str__(self):
        """
        Return string representation of the comment like.

        Returns:
            str: Formatted string showing user and comment information
        """
        return f"User {self.user.username} liked Comment {self.comment.id}"


class PostSaved(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="saved_posts")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_post_saved"),
        ]

    def __str__(self):
        return f"User {self.user.username} saved Post {self.post.id}"
