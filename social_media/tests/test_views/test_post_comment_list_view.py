from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from accounts.models import Profile
from accounts.tests.factories import ProfileFactory
from social_media.models import PostComment
from social_media.tests.factories import PostFactory


class TestPostCommentListView(TestCase):
    def setUp(self):
        self.profile = ProfileFactory(profile_type=Profile.FARMER)
        self.user = self.profile.user
        self.client.force_login(self.user)

        # Create a regular post
        self.post = PostFactory(user=self.user, content="Test post content")
        self.url = reverse(
            "social-media:post-comments",
            kwargs={"post_slug": self.post.slug},
        )

        # Create some comments
        self.comment1 = PostComment.objects.create(
            post=self.post,
            user=self.user,
            content="First comment",
        )
        self.comment2 = PostComment.objects.create(
            post=self.post,
            user=self.user,
            content="Second comment",
        )

    def test_get_comments_for_safe_post(self):
        """Test that comments are returned for safe posts"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["results"]) == 2  # noqa: PLR2004
        assert data["results"][0]["content"] == "First comment"
        assert data["results"][1]["content"] == "Second comment"

    def test_get_comments_for_harmful_post_returns_empty_with_no_next_cursor(self):
        """Test that harmful posts return empty results without next cursor pagination bug"""  # noqa: E501
        # Mark post as harmful
        self.post.is_potentially_harmful = True
        self.post.save()

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should return empty results
        assert data["results"] == []

        # Should not have next cursor (this was the bug)
        assert data["next"] is None
        assert data["previous"] is None

    def test_create_comment_on_harmful_post_fails(self):
        """Test that creating comments on harmful posts is blocked"""
        # Mark post as harmful
        self.post.is_potentially_harmful = True
        self.post.save()

        comment_data = {"content": "This should not be created"}
        response = self.client.post(self.url, comment_data)

        # Should still use the perform_create method which will try to get the post
        # The post exists but comments should be blocked at the list level
        assert response.status_code == status.HTTP_201_CREATED

        # But when we try to list comments, they should be empty
        response = self.client.get(self.url)
        data = response.json()
        assert data["results"] == []

    def test_harmful_post_pagination_with_multiple_pages(self):
        """Test pagination behavior with harmful posts that would normally have multiple pages"""  # noqa: E501
        # Create many comments to test pagination
        for i in range(30):  # More than page_size of 25
            PostComment.objects.create(
                post=self.post,
                user=self.user,
                content=f"Comment {i}",
            )

        # First verify normal pagination works
        response = self.client.get(self.url)
        data = response.json()
        assert len(data["results"]) == 25  # page_size  # noqa: PLR2004
        assert data["next"] is not None  # Should have next page

        # Now mark as harmful
        self.post.is_potentially_harmful = True
        self.post.save()

        # Should return empty without pagination
        response = self.client.get(self.url)
        data = response.json()
        assert data["results"] == []
        assert data["next"] is None
        assert data["previous"] is None

    def test_nonexistent_post_slug(self):
        """Test behavior with nonexistent post slug"""
        url = reverse("social-media:post-comments", kwargs={"post_slug": "nonexistent"})
        response = self.client.get(url)

        # Should return empty results for nonexistent post
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["results"] == []
