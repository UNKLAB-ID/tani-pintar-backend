from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.tests.factories import UserFactory
from social_media.models import PostSaved
from social_media.tests.factories import PostFactory
from social_media.tests.factories import PostSavedFactory


class TestPostSaveCreateView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.post = PostFactory()
        self.url = reverse(
            "social_media:post-save",
            kwargs={"slug": self.post.slug},
        )

    def test_post_save_create_success(self):
        """Test successful post save creation by authenticated user."""
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"message": "Post saved successfully"}
        assert PostSaved.objects.filter(post=self.post, user=self.user).exists()

    def test_post_save_create_duplicate_save(self):
        """Test that duplicate save returns error."""
        PostSavedFactory(post=self.post, user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "You have already saved this post"}
        assert PostSaved.objects.filter(post=self.post, user=self.user).count() == 1

    def test_post_save_create_post_not_found(self):
        """Test save creation with non-existent post returns 404."""
        self.client.force_login(self.user)
        url = reverse("social_media:post-save", kwargs={"slug": "non-existent"})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"error": "Post not found"}

    def test_post_save_create_unauthenticated(self):
        """Test that unauthenticated user cannot save a post."""
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not PostSaved.objects.filter(post=self.post).exists()

    def test_post_save_create_different_users(self):
        """Test that different users can save the same post."""
        self.client.force_login(self.user)
        response1 = self.client.post(self.url)

        self.client.force_login(self.other_user)
        response2 = self.client.post(self.url)

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert PostSaved.objects.filter(post=self.post).count() == 2  # noqa: PLR2004

    def test_post_save_create_response_format(self):
        """Test that response format is correct."""
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        assert "message" in response.json()
        assert isinstance(response.json()["message"], str)


class TestPostSaveDestroyView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.post = PostFactory()
        self.url = reverse(
            "social_media:post-unsave",
            kwargs={"slug": self.post.slug},
        )

    def test_post_unsave_success(self):
        """Test successful post unsave by authenticated user who saved the post."""
        post_saved = PostSavedFactory(post=self.post, user=self.user)
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Post unsaved successfully"}
        assert not PostSaved.objects.filter(id=post_saved.id).exists()

    def test_post_unsave_not_saved(self):
        """Test unsave when user hasn't saved the post returns error."""
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "You have not saved this post"}

    def test_post_unsave_post_not_found(self):
        """Test unsave with non-existent post returns 404."""
        self.client.force_login(self.user)
        url = reverse("social_media:post-unsave", kwargs={"slug": "non-existent"})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"error": "Post not found"}

    def test_post_unsave_unauthenticated(self):
        """Test that unauthenticated user cannot unsave a post."""
        PostSavedFactory(post=self.post, user=self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert PostSaved.objects.filter(post=self.post, user=self.user).exists()

    def test_post_unsave_different_user_save(self):
        """Test that user cannot unsave post saved by another user."""
        PostSavedFactory(post=self.post, user=self.other_user)
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "You have not saved this post"}
        assert PostSaved.objects.filter(post=self.post, user=self.other_user).exists()

    def test_post_unsave_response_format(self):
        """Test that response format is correct."""
        PostSavedFactory(post=self.post, user=self.user)
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert "message" in response.json()
        assert isinstance(response.json()["message"], str)

    def test_post_unsave_only_removes_user_save(self):
        """Test that unsave only removes the current user's save, not others."""
        user_saved = PostSavedFactory(post=self.post, user=self.user)
        other_saved = PostSavedFactory(post=self.post, user=self.other_user)

        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert not PostSaved.objects.filter(id=user_saved.id).exists()
        assert PostSaved.objects.filter(id=other_saved.id).exists()


class TestPostSaveEndpointsIntegration(TestCase):
    """Integration tests for save/unsave workflow."""

    def setUp(self):
        self.user = UserFactory()
        self.post = PostFactory()
        self.save_url = reverse(
            "social_media:post-save",
            kwargs={"slug": self.post.slug},
        )
        self.unsave_url = reverse(
            "social_media:post-unsave",
            kwargs={"slug": self.post.slug},
        )
        self.client.force_login(self.user)

    def test_save_unsave_workflow(self):
        """Test complete save and unsave workflow."""
        # Initially no saves
        assert PostSaved.objects.filter(post=self.post, user=self.user).count() == 0

        # Save the post
        save_response = self.client.post(self.save_url)
        assert save_response.status_code == status.HTTP_201_CREATED
        assert PostSaved.objects.filter(post=self.post, user=self.user).count() == 1

        # Unsave the post
        unsave_response = self.client.delete(self.unsave_url)
        assert unsave_response.status_code == status.HTTP_200_OK
        assert PostSaved.objects.filter(post=self.post, user=self.user).count() == 0

        # Save again after unsave
        save_again_response = self.client.post(self.save_url)
        assert save_again_response.status_code == status.HTTP_201_CREATED
        assert PostSaved.objects.filter(post=self.post, user=self.user).count() == 1

    def test_multiple_save_attempts(self):
        """Test multiple save attempts on same post."""
        # First save succeeds
        response1 = self.client.post(self.save_url)
        assert response1.status_code == status.HTTP_201_CREATED

        # Second save fails
        response2 = self.client.post(self.save_url)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

        # Third save still fails
        response3 = self.client.post(self.save_url)
        assert response3.status_code == status.HTTP_400_BAD_REQUEST

        # Only one save exists
        assert PostSaved.objects.filter(post=self.post, user=self.user).count() == 1

    def test_multiple_unsave_attempts(self):
        """Test multiple unsave attempts on same post."""
        # Create initial save
        PostSavedFactory(post=self.post, user=self.user)

        # First unsave succeeds
        response1 = self.client.delete(self.unsave_url)
        assert response1.status_code == status.HTTP_200_OK

        # Second unsave fails
        response2 = self.client.delete(self.unsave_url)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

        # Third unsave still fails
        response3 = self.client.delete(self.unsave_url)
        assert response3.status_code == status.HTTP_400_BAD_REQUEST

        # No saves exist
        assert PostSaved.objects.filter(post=self.post, user=self.user).count() == 0
