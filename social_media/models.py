from django.core.exceptions import ValidationError
from django.db import models
from django.utils.crypto import get_random_string

from core.users.models import User


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=15, unique=True)
    content = models.TextField()

    likes = models.ManyToManyField(
        User,
        related_name="liked_posts",
        blank=True,
        db_index=True,
    )
    shared_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

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
