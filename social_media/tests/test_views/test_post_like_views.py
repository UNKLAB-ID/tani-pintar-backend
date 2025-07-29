from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.tests.factories import UserFactory
from social_media.models import PostLike
from social_media.tests.factories import PostFactory
from social_media.tests.factories import PostLikeFactory


class TestPostLikeCreateView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.post = PostFactory()
        self.url = reverse(
            "social_media:post-like",
            kwargs={"slug": self.post.slug},
        )

    def test_post_like_create_success(self):
        """Test successful post like creation by authenticated user."""
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"message": "Post liked successfully"}
        assert PostLike.objects.filter(post=self.post, user=self.user).exists()

    def test_post_like_create_duplicate_like(self):
        """Test that duplicate like returns error."""
        PostLikeFactory(post=self.post, user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "You have already liked this post"}
        assert PostLike.objects.filter(post=self.post, user=self.user).count() == 1

    def test_post_like_create_post_not_found(self):
        """Test like creation with non-existent post returns 404."""
        self.client.force_login(self.user)
        url = reverse("social_media:post-like", kwargs={"slug": "non-existent"})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"error": "Post not found"}

    def test_post_like_create_unauthenticated(self):
        """Test that unauthenticated user cannot like a post."""
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not PostLike.objects.filter(post=self.post).exists()

    def test_post_like_create_different_users(self):
        """Test that different users can like the same post."""
        self.client.force_login(self.user)
        response1 = self.client.post(self.url)

        self.client.force_login(self.other_user)
        response2 = self.client.post(self.url)

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert PostLike.objects.filter(post=self.post).count() == 2  # noqa: PLR2004

    def test_post_like_create_response_format(self):
        """Test that response format is correct."""
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        assert "message" in response.json()
        assert isinstance(response.json()["message"], str)


class TestPostLikeDestroyView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.post = PostFactory()
        self.url = reverse(
            "social_media:post-unlike",
            kwargs={"slug": self.post.slug},
        )

    def test_post_unlike_success(self):
        """Test successful post unlike by authenticated user who liked the post."""
        post_like = PostLikeFactory(post=self.post, user=self.user)
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Post unliked successfully"}
        assert not PostLike.objects.filter(id=post_like.id).exists()

    def test_post_unlike_not_liked(self):
        """Test unlike when user hasn't liked the post returns error."""
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "You have not liked this post"}

    def test_post_unlike_post_not_found(self):
        """Test unlike with non-existent post returns 404."""
        self.client.force_login(self.user)
        url = reverse("social_media:post-unlike", kwargs={"slug": "non-existent"})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"error": "Post not found"}

    def test_post_unlike_unauthenticated(self):
        """Test that unauthenticated user cannot unlike a post."""
        PostLikeFactory(post=self.post, user=self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert PostLike.objects.filter(post=self.post, user=self.user).exists()

    def test_post_unlike_different_user_like(self):
        """Test that user cannot unlike post liked by another user."""
        PostLikeFactory(post=self.post, user=self.other_user)
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "You have not liked this post"}
        assert PostLike.objects.filter(post=self.post, user=self.other_user).exists()

    def test_post_unlike_response_format(self):
        """Test that response format is correct."""
        PostLikeFactory(post=self.post, user=self.user)
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert "message" in response.json()
        assert isinstance(response.json()["message"], str)

    def test_post_unlike_only_removes_user_like(self):
        """Test that unlike only removes the current user's like, not others."""
        user_like = PostLikeFactory(post=self.post, user=self.user)
        other_like = PostLikeFactory(post=self.post, user=self.other_user)

        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert not PostLike.objects.filter(id=user_like.id).exists()
        assert PostLike.objects.filter(id=other_like.id).exists()


class TestPostLikeEndpointsIntegration(TestCase):
    """Integration tests for like/unlike workflow."""

    def setUp(self):
        self.user = UserFactory()
        self.post = PostFactory()
        self.like_url = reverse(
            "social_media:post-like",
            kwargs={"slug": self.post.slug},
        )
        self.unlike_url = reverse(
            "social_media:post-unlike",
            kwargs={"slug": self.post.slug},
        )
        self.client.force_login(self.user)

    def test_like_unlike_workflow(self):
        """Test complete like and unlike workflow."""
        # Initially no likes
        assert PostLike.objects.filter(post=self.post, user=self.user).count() == 0

        # Like the post
        like_response = self.client.post(self.like_url)
        assert like_response.status_code == status.HTTP_201_CREATED
        assert PostLike.objects.filter(post=self.post, user=self.user).count() == 1

        # Unlike the post
        unlike_response = self.client.delete(self.unlike_url)
        assert unlike_response.status_code == status.HTTP_200_OK
        assert PostLike.objects.filter(post=self.post, user=self.user).count() == 0

        # Like again after unlike
        like_again_response = self.client.post(self.like_url)
        assert like_again_response.status_code == status.HTTP_201_CREATED
        assert PostLike.objects.filter(post=self.post, user=self.user).count() == 1

    def test_multiple_like_attempts(self):
        """Test multiple like attempts on same post."""
        # First like succeeds
        response1 = self.client.post(self.like_url)
        assert response1.status_code == status.HTTP_201_CREATED

        # Second like fails
        response2 = self.client.post(self.like_url)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

        # Third like still fails
        response3 = self.client.post(self.like_url)
        assert response3.status_code == status.HTTP_400_BAD_REQUEST

        # Only one like exists
        assert PostLike.objects.filter(post=self.post, user=self.user).count() == 1

    def test_multiple_unlike_attempts(self):
        """Test multiple unlike attempts on same post."""
        # Create initial like
        PostLikeFactory(post=self.post, user=self.user)

        # First unlike succeeds
        response1 = self.client.delete(self.unlike_url)
        assert response1.status_code == status.HTTP_200_OK

        # Second unlike fails
        response2 = self.client.delete(self.unlike_url)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

        # Third unlike still fails
        response3 = self.client.delete(self.unlike_url)
        assert response3.status_code == status.HTTP_400_BAD_REQUEST

        # No likes exist
        assert PostLike.objects.filter(post=self.post, user=self.user).count() == 0
