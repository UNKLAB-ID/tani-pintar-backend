from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.tests.factories import UserFactory
from social_media.models import PostCommentLike
from social_media.tests.factories import PostCommentFactory
from social_media.tests.factories import PostCommentLikeFactory
from social_media.tests.factories import PostFactory


class TestPostCommentLikeCreateView(TestCase):
    """
    Test suite for PostCommentLikeCreateView.

    Tests comment like creation functionality including successful likes,
    duplicate prevention, authentication requirements, and error handling.
    """

    def setUp(self):
        """Set up test data for comment like creation tests."""
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.post = PostFactory()
        self.comment = PostCommentFactory(post=self.post)
        self.url = reverse(
            "social_media:post-comment-like",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": self.comment.id,
            },
        )

    def test_comment_like_create_success(self):
        """Test successful comment like creation by authenticated user."""
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"message": "Comment liked successfully"}
        assert PostCommentLike.objects.filter(
            comment=self.comment,
            user=self.user,
        ).exists()

    def test_comment_like_create_duplicate_like(self):
        """Test that duplicate comment like returns error."""
        PostCommentLikeFactory(comment=self.comment, user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "You have already liked this comment"}
        assert (
            PostCommentLike.objects.filter(
                comment=self.comment,
                user=self.user,
            ).count()
            == 1
        )

    def test_comment_like_create_comment_not_found(self):
        """Test like creation with non-existent comment returns 404."""
        self.client.force_login(self.user)
        url = reverse(
            "social_media:post-comment-like",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": 99999,  # Non-existent comment ID
            },
        )
        response = self.client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_comment_like_create_post_not_found(self):
        """Test like creation with non-existent post returns 404."""
        self.client.force_login(self.user)
        url = reverse(
            "social_media:post-comment-like",
            kwargs={
                "post_slug": "non-existent-slug",
                "comment_id": self.comment.id,
            },
        )
        response = self.client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_comment_like_create_unauthenticated(self):
        """Test that unauthenticated user cannot like a comment."""
        response = self.client.post(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not PostCommentLike.objects.filter(comment=self.comment).exists()

    def test_comment_like_create_different_users(self):
        """Test that different users can like the same comment."""
        self.client.force_login(self.user)
        response1 = self.client.post(self.url)

        self.client.force_login(self.other_user)
        response2 = self.client.post(self.url)

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert PostCommentLike.objects.filter(comment=self.comment).count() == 2  # noqa: PLR2004

    def test_comment_like_create_response_format(self):
        """Test that response format is correct."""
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        assert "message" in response.json()
        assert isinstance(response.json()["message"], str)

    def test_comment_like_create_wrong_post_comment_mismatch(self):
        """Test like creation when comment doesn't belong to specified post."""
        different_post = PostFactory()
        different_comment = PostCommentFactory(post=different_post)

        # Try to like a comment using wrong post slug
        url = reverse(
            "social_media:post-comment-like",
            kwargs={
                "post_slug": self.post.slug,  # Wrong post
                "comment_id": different_comment.id,
            },
        )

        self.client.force_login(self.user)
        response = self.client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_comment_like_create_multiple_comments_same_post(self):
        """Test user can like multiple comments on the same post."""
        comment2 = PostCommentFactory(post=self.post)
        url2 = reverse(
            "social_media:post-comment-like",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": comment2.id,
            },
        )

        self.client.force_login(self.user)

        # Like first comment
        response1 = self.client.post(self.url)
        # Like second comment
        response2 = self.client.post(url2)

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert PostCommentLike.objects.filter(user=self.user).count() == 2  # noqa: PLR2004


class TestPostCommentLikeDestroyView(TestCase):
    """
    Test suite for PostCommentLikeDestroyView.

    Tests comment unlike functionality including successful unlikes,
    error handling for non-existent likes, authentication requirements,
    and permission validation.
    """

    def setUp(self):
        """Set up test data for comment unlike tests."""
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.post = PostFactory()
        self.comment = PostCommentFactory(post=self.post)
        self.url = reverse(
            "social_media:post-comment-unlike",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": self.comment.id,
            },
        )

    def test_comment_unlike_success(self):
        """Test successful comment unlike by authenticated user who liked the comment."""  # noqa: E501
        comment_like = PostCommentLikeFactory(comment=self.comment, user=self.user)
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Comment unliked successfully"}
        assert not PostCommentLike.objects.filter(id=comment_like.id).exists()

    def test_comment_unlike_not_liked(self):
        """Test unlike when user hasn't liked the comment returns error."""
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "You have not liked this comment"}

    def test_comment_unlike_comment_not_found(self):
        """Test unlike with non-existent comment returns 404."""
        self.client.force_login(self.user)
        url = reverse(
            "social_media:post-comment-unlike",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": 99999,  # Non-existent comment ID
            },
        )
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_comment_unlike_post_not_found(self):
        """Test unlike with non-existent post returns 404."""
        self.client.force_login(self.user)
        url = reverse(
            "social_media:post-comment-unlike",
            kwargs={
                "post_slug": "non-existent-slug",
                "comment_id": self.comment.id,
            },
        )
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_comment_unlike_unauthenticated(self):
        """Test that unauthenticated user cannot unlike a comment."""
        PostCommentLikeFactory(comment=self.comment, user=self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert PostCommentLike.objects.filter(
            comment=self.comment,
            user=self.user,
        ).exists()

    def test_comment_unlike_different_user_like(self):
        """Test that user cannot unlike comment liked by another user."""
        PostCommentLikeFactory(comment=self.comment, user=self.other_user)
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "You have not liked this comment"}
        assert PostCommentLike.objects.filter(
            comment=self.comment,
            user=self.other_user,
        ).exists()

    def test_comment_unlike_response_format(self):
        """Test that response format is correct."""
        PostCommentLikeFactory(comment=self.comment, user=self.user)
        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert "message" in response.json()
        assert isinstance(response.json()["message"], str)

    def test_comment_unlike_only_removes_user_like(self):
        """Test that unlike only removes the current user's like, not others."""
        user_like = PostCommentLikeFactory(comment=self.comment, user=self.user)
        other_like = PostCommentLikeFactory(comment=self.comment, user=self.other_user)

        self.client.force_login(self.user)
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert not PostCommentLike.objects.filter(id=user_like.id).exists()
        assert PostCommentLike.objects.filter(id=other_like.id).exists()

    def test_comment_unlike_wrong_post_comment_mismatch(self):
        """Test unlike when comment doesn't belong to specified post."""
        different_post = PostFactory()
        different_comment = PostCommentFactory(post=different_post)
        PostCommentLikeFactory(comment=different_comment, user=self.user)

        # Try to unlike a comment using wrong post slug
        url = reverse(
            "social_media:post-comment-unlike",
            kwargs={
                "post_slug": self.post.slug,  # Wrong post
                "comment_id": different_comment.id,
            },
        )

        self.client.force_login(self.user)
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPostCommentLikeEndpointsIntegration(TestCase):
    """
    Integration tests for comment like/unlike workflow.

    Tests the complete lifecycle of comment likes including like creation,
    unlike operations, and various workflow scenarios.
    """

    def setUp(self):
        """Set up test data for integration tests."""
        self.user = UserFactory()
        self.post = PostFactory()
        self.comment = PostCommentFactory(post=self.post)
        self.like_url = reverse(
            "social_media:post-comment-like",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": self.comment.id,
            },
        )
        self.unlike_url = reverse(
            "social_media:post-comment-unlike",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": self.comment.id,
            },
        )
        self.client.force_login(self.user)

    def test_like_unlike_workflow(self):
        """Test complete like and unlike workflow."""
        # Initially no likes
        assert (
            PostCommentLike.objects.filter(
                comment=self.comment,
                user=self.user,
            ).count()
            == 0
        )

        # Like the comment
        like_response = self.client.post(self.like_url)
        assert like_response.status_code == status.HTTP_201_CREATED
        assert (
            PostCommentLike.objects.filter(
                comment=self.comment,
                user=self.user,
            ).count()
            == 1
        )

        # Unlike the comment
        unlike_response = self.client.delete(self.unlike_url)
        assert unlike_response.status_code == status.HTTP_200_OK
        assert (
            PostCommentLike.objects.filter(
                comment=self.comment,
                user=self.user,
            ).count()
            == 0
        )

        # Like again after unlike
        like_again_response = self.client.post(self.like_url)
        assert like_again_response.status_code == status.HTTP_201_CREATED
        assert (
            PostCommentLike.objects.filter(
                comment=self.comment,
                user=self.user,
            ).count()
            == 1
        )

    def test_multiple_like_attempts(self):
        """Test multiple like attempts on same comment."""
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
        assert (
            PostCommentLike.objects.filter(
                comment=self.comment,
                user=self.user,
            ).count()
            == 1
        )

    def test_multiple_unlike_attempts(self):
        """Test multiple unlike attempts on same comment."""
        # Create initial like
        PostCommentLikeFactory(comment=self.comment, user=self.user)

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
        assert (
            PostCommentLike.objects.filter(
                comment=self.comment,
                user=self.user,
            ).count()
            == 0
        )

    def test_like_multiple_comments_workflow(self):
        """Test liking multiple comments on the same post."""
        comment2 = PostCommentFactory(post=self.post)
        comment3 = PostCommentFactory(post=self.post)

        like_url2 = reverse(
            "social_media:post-comment-like",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": comment2.id,
            },
        )
        like_url3 = reverse(
            "social_media:post-comment-like",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": comment3.id,
            },
        )

        # Like all three comments
        response1 = self.client.post(self.like_url)
        response2 = self.client.post(like_url2)
        response3 = self.client.post(like_url3)

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert response3.status_code == status.HTTP_201_CREATED

        # Verify all likes exist
        assert PostCommentLike.objects.filter(user=self.user).count() == 3  # noqa: PLR2004

    def test_nested_comment_like_workflow(self):
        """Test liking parent and child comments."""
        # Create a nested comment (reply to the original comment)
        reply_comment = PostCommentFactory(post=self.post, parent=self.comment)

        reply_like_url = reverse(
            "social_media:post-comment-like",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": reply_comment.id,
            },
        )

        # Like both parent and child comments
        parent_response = self.client.post(self.like_url)
        child_response = self.client.post(reply_like_url)

        assert parent_response.status_code == status.HTTP_201_CREATED
        assert child_response.status_code == status.HTTP_201_CREATED

        # Verify both likes exist
        assert PostCommentLike.objects.filter(
            comment=self.comment,
            user=self.user,
        ).exists()
        assert PostCommentLike.objects.filter(
            comment=reply_comment,
            user=self.user,
        ).exists()
