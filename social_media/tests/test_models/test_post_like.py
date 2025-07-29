import pytest
from django.db import IntegrityError
from django.test import TestCase

from social_media.models import PostLike
from social_media.tests.factories import PostFactory
from social_media.tests.factories import PostLikeFactory


class PostLikeModelTest(TestCase):
    def setUp(self):
        self.post = PostFactory()
        self.post_like = PostLikeFactory(post=self.post)
        self.second_post = PostFactory()

    def test_post_like_creation(self):
        """Test that PostLike can be created successfully."""
        assert self.post_like.post == self.post
        assert self.post_like.user is not None
        assert self.post_like.created_at is not None

    def test_post_like_str_representation(self):
        """Test the string representation of PostLike."""
        expected_str = (
            f"User {self.post_like.user.username} liked Post {self.post_like.post.id}"
        )
        assert str(self.post_like) == expected_str

    def test_post_like_fields(self):
        """Test that all required fields are properly set."""
        assert self.post_like.post is not None
        assert self.post_like.user is not None
        assert hasattr(self.post_like, "created_at")

    def test_unique_constraint_post_user(self):
        """Test that the same user cannot like the same post twice."""
        with pytest.raises(IntegrityError):
            PostLikeFactory(post=self.post, user=self.post_like.user)

    def test_user_can_like_different_posts(self):
        """Test that the same user can like different posts."""
        second_like = PostLikeFactory(post=self.second_post, user=self.post_like.user)
        assert second_like.post == self.second_post
        assert second_like.user == self.post_like.user

    def test_different_users_can_like_same_post(self):
        """Test that different users can like the same post."""
        second_like = PostLikeFactory(post=self.post)
        assert second_like.post == self.post
        assert second_like.user != self.post_like.user

    def test_post_likes_related_name(self):
        """Test that the related name 'likes' works correctly."""
        likes = self.post.likes.all()
        assert self.post_like in likes
        assert len(likes) == 1

    def test_cascade_delete_post(self):
        """Test that deleting a post also deletes related PostLike instances."""
        post_like_id = self.post_like.id
        self.post.delete()

        assert not PostLike.objects.filter(id=post_like_id).exists()

    def test_cascade_delete_user(self):
        """Test that deleting a user also deletes related PostLike instances."""
        user = self.post_like.user
        post_like_id = self.post_like.id
        user.delete()

        assert not PostLike.objects.filter(id=post_like_id).exists()

    def test_created_at_auto_generation(self):
        """Test that created_at is automatically set when creating a PostLike."""
        new_like = PostLikeFactory()
        assert new_like.created_at is not None

    def test_multiple_likes_on_different_posts(self):
        """Test creating multiple likes for different posts by the same user."""
        user = self.post_like.user

        # Create likes for different posts
        second_like = PostLikeFactory(post=self.second_post, user=user)
        third_post = PostFactory()
        third_like = PostLikeFactory(post=third_post, user=user)

        # Verify all likes exist
        user_likes = PostLike.objects.filter(user=user)
        assert len(user_likes) == 3  # noqa: PLR2004
        assert self.post_like in user_likes
        assert second_like in user_likes
        assert third_like in user_likes

    def test_post_likes_count(self):
        """Test counting likes for a post."""
        # Add more likes to the post
        PostLikeFactory(post=self.post)
        PostLikeFactory(post=self.post)

        likes_count = self.post.likes.count()
        assert likes_count == 3  # noqa: PLR2004
