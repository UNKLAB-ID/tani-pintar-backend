from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.crypto import get_random_string

from core.users.models import User


class PostQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        """
        Filter posts based on privacy settings and user relationships.

        This method implements the core privacy logic for the social media platform,
        determining which posts a given user can see based on their authentication
        status, relationship with post authors, and post privacy settings.

        Privacy Rules:
            - Anonymous users: Only PUBLIC posts
            - Authenticated users: PUBLIC posts + own posts + FRIENDS posts from mutual followers
            - ONLY_ME posts: Only visible to the post author

        Args:
            user (User | None): The user requesting to view posts. Can be None for
                anonymous users or unauthenticated requests.

        Returns:
            QuerySet[Post]: Filtered queryset containing only posts visible to the user.

        Performance Notes:
            - Uses database indexes on privacy field for efficient filtering
            - Performs 3 database queries for mutual follower detection
            - Consider caching friendship relationships for high-traffic scenarios

        Examples:
            # Get posts visible to anonymous user
            visible_posts = Post.objects.visible_to_user(None)

            # Get posts visible to authenticated user
            visible_posts = Post.objects.visible_to_user(request.user)

            # Use in views with additional filtering
            posts = Post.objects.visible_to_user(request.user).filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            )
        """  # noqa: E501
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
        except (AttributeError, User.profile.RelatedObjectDoesNotExist):
            # User has no profile or profile doesn't exist, can only see public posts
            return self.filter(privacy=Post.PUBLIC)

        # Get friend user IDs (mutual followers)
        # Find users where both follow each other
        from accounts.models import Follow

        # Get profiles this user follows
        following_profiles = Follow.objects.filter(
            follower=user_profile,
        ).values_list("following", flat=True)

        # Get profiles that follow this user back (mutual followers = friends)
        friend_profile_ids = Follow.objects.filter(
            follower__in=following_profiles,
            following=user_profile,
        ).values_list("follower", flat=True)

        # Convert profile IDs to user IDs
        from accounts.models import Profile

        friend_user_ids = Profile.objects.filter(
            id__in=friend_profile_ids,
        ).values_list("user_id", flat=True)

        return self.filter(
            Q(privacy=Post.PUBLIC)  # Public posts
            | Q(user=user)  # Own posts
            | Q(privacy=Post.FRIENDS, user_id__in=friend_user_ids),  # Friends' posts
        )


class PostManager(models.Manager):
    """
    Custom manager for Post model that provides privacy-aware query methods.

    This manager extends Django's default Manager to include privacy filtering
    capabilities, making it easy to retrieve posts that respect privacy settings
    and user relationships throughout the application.

    The manager uses PostQuerySet to provide consistent privacy filtering
    across all Post queries, ensuring that privacy rules are enforced at the
    database level rather than in application logic.

    Methods:
        get_queryset(): Returns PostQuerySet instead of default QuerySet
        visible_to_user(user): Convenience method for privacy-filtered posts

    Usage:
        # Get all posts visible to a user
        posts = Post.objects.visible_to_user(request.user)

        # Chain with other querysets methods
        recent_posts = Post.objects.visible_to_user(request.user).filter(
            created_at__gte=last_week
        )
    """

    def get_queryset(self):
        """
        Return PostQuerySet with privacy filtering capabilities.

        Returns:
            PostQuerySet: Custom queryset with visible_to_user() method.
        """
        return PostQuerySet(self.model, using=self._db)

    def visible_to_user(self, user):
        """
        Get posts visible to the specified user based on privacy settings.

        This is a convenience method that delegates to PostQuerySet.visible_to_user()
        for consistent privacy filtering across the application.

        Args:
            user (User | None): The user to filter posts for.

        Returns:
            QuerySet[Post]: Posts visible to the specified user.
        """
        return self.get_queryset().visible_to_user(user)


class Post(models.Model):
    """
    Social media post model with privacy settings and engagement tracking.

    This model represents user-generated posts in the social media platform,
    supporting three privacy levels to control post visibility. Posts can be
    public, visible to friends only, or private to the author.

    Privacy Levels:
        PUBLIC: Visible to all users (authenticated and anonymous)
        FRIENDS: Visible to mutual followers and the post author
        ONLY_ME: Visible only to the post author

    The model uses a custom manager (PostManager) that provides privacy-aware
    queries to ensure posts are only shown to authorized users.

    Attributes:
        privacy (CharField): Controls post visibility with indexed field for performance
        slug (SlugField): Unique identifier for URL-friendly post access
        content (TextField): The main post content
        user (ForeignKey): The author of the post
        shared_count (PositiveIntegerField): Track post sharing metrics
        is_potentially_harmful (BooleanField): Content moderation flag
        created_at/updated_at (DateTimeField): Timestamp tracking

    Related Models:
        - PostImage: Images attached to the post
        - PostComment: Comments on the post
        - PostLike: User likes on the post
        - PostView: View tracking for analytics
        - PostSaved: User bookmarks of the post
    """

    # Privacy level constants
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
        db_index=True,
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


class Report(models.Model):
    """
    Model representing a user report of a post for policy violations.

    This model tracks when users report posts for various reasons such as spam,
    hate speech, violence, etc. Each user can only report a post once, and the
    system tracks the approval status and moderation actions.

    Report Reasons:
        SP: Spam - Unsolicited or repetitive content
        HR: Hate Speech - Content promoting hatred or discrimination
        VL: Violence - Content depicting or promoting violence
        NU: Nudity - Inappropriate sexual or nude content
        MI: Misinformation - False or misleading information
        BU: Bullying - Content targeting individuals with harassment
        OT: Other - Other policy violations not covered above

    Attributes:
        post (ForeignKey): The post being reported
        user (ForeignKey): The user who made the report
        reason (CharField): Two-letter code indicating the report reason
        detail_reason (TextField): Optional additional explanation from reporter
        restrict_user (BooleanField): Whether reporter wants to hide content from this
        post author
        block_user (BooleanField): Whether reporter wants to block the post
        author entirely
        is_approved (BooleanField): Whether a moderator has approved this report
        approved_by (CharField): Username/ID of moderator who approved the report
        created_at (DateTimeField): When the report was created
        created_by (CharField): Username/ID of the user who created the report
        updated_at (DateTimeField): Last time the report status was updated
        updated_by (CharField): Username/ID of who last updated the report

    Constraints:
        - Unique constraint on (post, user) to prevent duplicate reports
        - Cascade delete when post is deleted
        - Database indexes on reason, is_approved, and created_at for admin filtering
    """

    # Report reason choices
    SPAM = "SP"
    HATE_SPEECH = "HS"
    VIOLENCE = "VL"
    NUDITY = "NU"
    MISINFORMATION = "MI"
    BULLYING = "BU"
    OTHER = "OT"

    REASON_CHOICES = [
        (SPAM, "Spam"),
        (HATE_SPEECH, "Hate Speech"),
        (VIOLENCE, "Violence"),
        (NUDITY, "Nudity"),
        (MISINFORMATION, "Misinformation"),
        (BULLYING, "Bullying"),
        (OTHER, "Other"),
    ]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="reports",
        help_text="The post being reported",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports_made",
        help_text="The user who made the report",
    )
    reason = models.CharField(
        max_length=2,
        choices=REASON_CHOICES,
        help_text="Reason code for the report",
        db_index=True,
    )
    detail_reason = models.TextField(
        blank=True,
        help_text="Optional additional explanation from the reporter",
    )
    restrict_user = models.BooleanField(
        default=False,
        help_text="Whether reporter wants to hide content from this post author",
    )
    block_user = models.BooleanField(
        default=False,
        help_text="Whether reporter wants to block the post author entirely",
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="Whether a moderator has approved this report",
        db_index=True,
    )
    approved_by = models.CharField(
        max_length=150,
        blank=True,
        help_text="Username/ID of moderator who approved the report",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the report was created",
    )
    created_by = models.CharField(
        max_length=150,
        help_text="Username/ID of the user who created the report",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last time the report status was updated",
    )
    updated_by = models.CharField(
        max_length=150,
        blank=True,
        help_text="Username/ID of who last updated the report",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"],
                name="unique_post_report",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        """
        Return string representation of the report.

        Returns:
            str: Formatted string showing user, post, and reason
            information
        """
        return (
            f"Report by {self.user.username} on Post {self.post.slug} - "
            f"{self.get_reason_display()}"
        )

    def save(self, *args, **kwargs):
        """
        Override save method to automatically set created_by field.

        This ensures that the created_by field is always populated with the
        username of the user making the report for audit purposes.
        """
        if not self.created_by:
            self.created_by = self.user.username
        super().save(*args, **kwargs)

    def approve(self, moderator_user):
        """
        Approve the report and mark who approved it.

        Args:
            moderator_user (User): The moderator approving the report

        Returns:
            bool: True if the report was successfully approved
        """
        self.is_approved = True
        self.approved_by = moderator_user.username
        self.updated_by = moderator_user.username
        self.save()
        return True
