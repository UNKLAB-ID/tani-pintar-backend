import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from accounts.models import Profile
from accounts.tests.factories import ProfileFactory
from social_media.tests.factories import PostCommentFactory
from social_media.tests.factories import PostFactory


class TestPostCommentUpdateView(TestCase):
    """Test cases for updating comments via PUT/PATCH requests."""

    def setUp(self):
        self.profile = ProfileFactory(profile_type=Profile.FARMER)
        self.user = self.profile.user
        self.client.force_login(self.user)

        # Create a post and comment
        self.post = PostFactory(user=self.user, content="Test post content")
        self.comment = PostCommentFactory(
            post=self.post,
            user=self.user,
            content="Original comment content",
        )
        self.url = reverse(
            "social-media:post-comment-update",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": self.comment.id,
            },
        )

        # Create another user for unauthorized access tests
        self.other_profile = ProfileFactory(profile_type=Profile.FARMER)
        self.other_user = self.other_profile.user

    def test_update_comment_success_put(self):
        """Test successfully updating comment content with PUT method"""
        updated_data = {"content": "Updated comment content"}
        response = self.client.put(
            self.url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == "Updated comment content"

        # Verify in database
        self.comment.refresh_from_db()
        assert self.comment.content == "Updated comment content"

    def test_update_comment_success_patch(self):
        """Test successfully updating comment content with PATCH method"""
        updated_data = {"content": "Patched comment content"}
        response = self.client.patch(
            self.url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == "Patched comment content"

        # Verify in database
        self.comment.refresh_from_db()
        assert self.comment.content == "Patched comment content"

    def test_update_comment_unauthorized_user(self):
        """Test that different user cannot update comment (should get 404)"""
        self.client.force_login(self.other_user)

        updated_data = {"content": "Should not be updated"}
        response = self.client.put(
            self.url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify comment content unchanged
        self.comment.refresh_from_db()
        assert self.comment.content == "Original comment content"

    def test_update_comment_unauthenticated(self):
        """Test that anonymous user cannot update comment (should get 403)"""
        self.client.logout()

        updated_data = {"content": "Should not be updated"}
        response = self.client.put(
            self.url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Verify comment content unchanged
        self.comment.refresh_from_db()
        assert self.comment.content == "Original comment content"

    def test_update_comment_nonexistent(self):
        """Test updating non-existent comment returns 404"""
        nonexistent_url = reverse(
            "social-media:post-comment-update",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": 99999,
            },
        )

        updated_data = {"content": "Should not work"}
        response = self.client.put(
            nonexistent_url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_comment_different_post_slug(self):
        """Test updating comment with wrong post_slug returns 404"""
        other_post = PostFactory(user=self.user)
        wrong_url = reverse(
            "social-media:post-comment-update",
            kwargs={
                "post_slug": other_post.slug,
                "comment_id": self.comment.id,
            },
        )

        updated_data = {"content": "Should not work"}
        response = self.client.put(
            wrong_url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify comment content unchanged
        self.comment.refresh_from_db()
        assert self.comment.content == "Original comment content"


class TestPostCommentUpdateValidation(TestCase):
    """Test cases for comment update content validation."""

    def setUp(self):
        self.profile = ProfileFactory(profile_type=Profile.FARMER)
        self.user = self.profile.user
        self.client.force_login(self.user)

        self.post = PostFactory(user=self.user)
        self.comment = PostCommentFactory(
            post=self.post,
            user=self.user,
            content="Original content",
        )
        self.url = reverse(
            "social-media:post-comment-update",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": self.comment.id,
            },
        )

    def test_update_comment_empty_content_fails(self):
        """Test that updating with empty content fails validation"""
        updated_data = {"content": ""}
        response = self.client.put(
            self.url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "content" in data
        assert "Content cannot be empty." in str(data["content"])

        # Verify comment content unchanged
        self.comment.refresh_from_db()
        assert self.comment.content == "Original content"

    def test_update_comment_whitespace_only_fails(self):
        """Test that updating with whitespace-only content fails"""
        updated_data = {"content": "   \n\t   "}
        response = self.client.put(
            self.url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "content" in data
        assert "Content cannot be empty." in str(data["content"])

        # Verify comment content unchanged
        self.comment.refresh_from_db()
        assert self.comment.content == "Original content"

    def test_update_comment_missing_content_fails(self):
        """Test that updating without content field fails"""
        updated_data = {}
        response = self.client.put(
            self.url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "content" in data

        # Verify comment content unchanged
        self.comment.refresh_from_db()
        assert self.comment.content == "Original content"

    def test_update_comment_long_content_succeeds(self):
        """Test that updating with very long content succeeds"""
        long_content = "A" * 1000  # 1000 character content
        updated_data = {"content": long_content}
        response = self.client.put(
            self.url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == long_content

        # Verify in database
        self.comment.refresh_from_db()
        assert self.comment.content == long_content


class TestPostCommentUpdatePermissions(TestCase):
    """Test cases for comment update security and permissions."""

    def setUp(self):
        self.profile = ProfileFactory(profile_type=Profile.FARMER)
        self.user = self.profile.user
        self.client.force_login(self.user)

        self.post = PostFactory(user=self.user)
        self.comment = PostCommentFactory(
            post=self.post,
            user=self.user,
            content="Original content",
        )
        self.url = reverse(
            "social-media:post-comment-update",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": self.comment.id,
            },
        )

    def test_update_comment_owner_only(self):
        """Test that only comment owner can update their comment"""
        # Create another user and their comment
        other_profile = ProfileFactory(profile_type=Profile.FARMER)
        other_user = other_profile.user
        other_comment = PostCommentFactory(
            post=self.post,
            user=other_user,
            content="Other user's comment",
        )

        # Try to update other user's comment
        other_url = reverse(
            "social-media:post-comment-update",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": other_comment.id,
            },
        )

        updated_data = {"content": "Should not be updated"}
        response = self.client.put(
            other_url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify other user's comment unchanged
        other_comment.refresh_from_db()
        assert other_comment.content == "Other user's comment"

    def test_update_comment_preserves_other_fields(self):
        """Test that update only changes content, preserves other fields"""
        original_user = self.comment.user
        original_post = self.comment.post
        original_parent = self.comment.parent
        original_created_at = self.comment.created_at

        updated_data = {"content": "Updated content only"}
        response = self.client.put(
            self.url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify only content changed
        self.comment.refresh_from_db()
        assert self.comment.content == "Updated content only"
        assert self.comment.user == original_user
        assert self.comment.post == original_post
        assert self.comment.parent == original_parent
        assert self.comment.created_at == original_created_at
        # updated_at should be changed
        assert self.comment.updated_at > original_created_at

    def test_update_reply_owner_only(self):
        """Test that reply updates also require ownership"""
        # Create a parent comment and reply
        parent_comment = PostCommentFactory(
            post=self.post,
            user=self.user,
            content="Parent comment",
        )
        reply = PostCommentFactory(
            post=self.post,
            user=self.user,
            content="Original reply",
            parent=parent_comment,
        )

        reply_url = reverse(
            "social-media:post-comment-update",
            kwargs={
                "post_slug": self.post.slug,
                "comment_id": reply.id,
            },
        )

        # Owner should be able to update
        updated_data = {"content": "Updated reply"}
        response = self.client.put(
            reply_url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify reply updated
        reply.refresh_from_db()
        assert reply.content == "Updated reply"
        assert reply.parent == parent_comment  # Parent relationship preserved

        # Create another user and try to update the reply
        other_profile = ProfileFactory(profile_type=Profile.FARMER)
        other_user = other_profile.user
        self.client.force_login(other_user)

        updated_data = {"content": "Should not be updated"}
        response = self.client.put(
            reply_url,
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify reply content unchanged
        reply.refresh_from_db()
        assert reply.content == "Updated reply"
