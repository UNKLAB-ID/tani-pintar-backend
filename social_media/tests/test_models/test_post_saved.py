import pytest
from django.db import IntegrityError
from django.test import TestCase

from social_media.models import PostSaved
from social_media.tests.factories import PostFactory
from social_media.tests.factories import PostSavedFactory


class PostSavedModelTest(TestCase):
    def setUp(self):
        self.post = PostFactory()
        self.post_saved = PostSavedFactory(post=self.post)
        self.second_post = PostFactory()

    def test_post_saved_creation(self):
        """Test that PostSaved can be created successfully."""
        assert self.post_saved.post == self.post
        assert self.post_saved.user is not None
        assert self.post_saved.created_at is not None

    def test_post_saved_str_representation(self):
        """Test the string representation of PostSaved."""
        expected_str = (
            f"User {self.post_saved.user.username} saved Post {self.post_saved.post.id}"
        )
        assert str(self.post_saved) == expected_str

    def test_post_saved_fields(self):
        """Test that all required fields are properly set."""
        assert self.post_saved.post is not None
        assert self.post_saved.user is not None
        assert hasattr(self.post_saved, "created_at")

    def test_unique_constraint_post_user(self):
        """Test that the same user cannot save the same post twice."""
        with pytest.raises(IntegrityError):
            PostSavedFactory(post=self.post, user=self.post_saved.user)

    def test_user_can_save_different_posts(self):
        """Test that the same user can save different posts."""
        second_saved = PostSavedFactory(
            post=self.second_post,
            user=self.post_saved.user,
        )
        assert second_saved.post == self.second_post
        assert second_saved.user == self.post_saved.user

    def test_different_users_can_save_same_post(self):
        """Test that different users can save the same post."""
        second_saved = PostSavedFactory(post=self.post)
        assert second_saved.post == self.post
        assert second_saved.user != self.post_saved.user

    def test_post_saved_posts_related_name(self):
        """Test that the related name 'saved_posts' works correctly."""
        saved_posts = self.post.saved_posts.all()
        assert self.post_saved in saved_posts
        assert len(saved_posts) == 1

    def test_cascade_delete_post(self):
        """Test that deleting a post also deletes related PostSaved instances."""
        post_saved_id = self.post_saved.id
        self.post.delete()

        assert not PostSaved.objects.filter(id=post_saved_id).exists()

    def test_cascade_delete_user(self):
        """Test that deleting a user also deletes related PostSaved instances."""
        user = self.post_saved.user
        post_saved_id = self.post_saved.id
        user.delete()

        assert not PostSaved.objects.filter(id=post_saved_id).exists()

    def test_created_at_auto_generation(self):
        """Test that created_at is automatically set when creating a PostSaved."""
        new_saved = PostSavedFactory()
        assert new_saved.created_at is not None

    def test_multiple_saves_on_different_posts(self):
        """Test creating multiple saves for different posts by the same user."""
        user = self.post_saved.user

        # Create saves for different posts
        second_saved = PostSavedFactory(post=self.second_post, user=user)
        third_post = PostFactory()
        third_saved = PostSavedFactory(post=third_post, user=user)

        # Verify all saves exist
        user_saves = PostSaved.objects.filter(user=user)
        assert len(user_saves) == 3  # noqa: PLR2004
        assert self.post_saved in user_saves
        assert second_saved in user_saves
        assert third_saved in user_saves

    def test_post_saved_posts_count(self):
        """Test counting saved posts for a post."""
        # Add more saves to the post
        PostSavedFactory(post=self.post)
        PostSavedFactory(post=self.post)

        saved_count = self.post.saved_posts.count()
        assert saved_count == 3  # noqa: PLR2004
