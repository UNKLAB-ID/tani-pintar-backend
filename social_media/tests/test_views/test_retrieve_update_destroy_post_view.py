from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from accounts.tests.factories import ProfileFactory
from social_media.tests.factories import PostFactory
from social_media.tests.factories import PostLikeFactory


class TestRetrieveUpdateDestroyPostView(TestCase):
    def setUp(self):
        self.user = ProfileFactory().user
        self.user_2 = ProfileFactory().user
        self.client.force_login(self.user)

        self.posts = PostFactory.create_batch(10, user=self.user)

    def test_retrieve_post(self):
        # Test that the user can retrieve the post
        response = self.client.get(
            reverse("social_media:post", kwargs={"slug": self.posts[0].slug}),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("content") is not None
        assert response.json().get("images") is not None
        assert response.json().get("user") is not None
        assert (
            "likes_count" in response.json()
        ), "Post detail should contain likes_count field"

    def test_update_post(self):
        # Test that the user can update the post
        response = self.client.put(
            reverse("social_media:post", kwargs={"slug": self.posts[0].slug}),
            data={"content": "New content"},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("content") == "New content"
        assert (
            "likes_count" in response.json()
        ), "Post update response should contain likes_count field"

        # Test that another user cannot update the post
        self.client.force_login(self.user_2)
        response = self.client.put(
            reverse("social_media:post", kwargs={"slug": self.posts[0].slug}),
            data={"content": "New content"},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_destroy_post(self):
        # Test that the user can delete the post
        response = self.client.delete(
            reverse("social_media:post", kwargs={"slug": self.posts[0].slug}),
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Test that another user cannot delete the post
        self.client.force_login(self.user_2)
        response = self.client.delete(
            reverse("social_media:post", kwargs={"slug": self.posts[1].slug}),
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test that the post is not found
        response = self.client.get(
            reverse("social_media:post", kwargs={"slug": self.posts[0].slug}),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_post_views_count(self):
        # Test that the views count is incremented
        self.client.get(
            reverse("social_media:post", kwargs={"slug": self.posts[0].slug}),
        )
        self.client.force_login(self.user_2)
        self.client.get(
            reverse("social_media:post", kwargs={"slug": self.posts[0].slug}),
        )

        response = self.client.get(
            reverse("social_media:post", kwargs={"slug": self.posts[0].slug}),
        )
        assert response.json().get("views_count") == 2  # noqa: PLR2004

    def test_post_detail_likes_count_accuracy(self):
        """Test that likes_count field shows accurate count of likes in detail view."""
        # Create a post with no likes
        post_no_likes = PostFactory(user=self.user)

        # Create a post with likes
        post_with_likes = PostFactory(user=self.user)
        PostLikeFactory.create_batch(3, post=post_with_likes)

        # Test post with no likes
        response = self.client.get(
            reverse("social_media:post", kwargs={"slug": post_no_likes.slug}),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("likes_count") == 0

        # Test post with likes
        response = self.client.get(
            reverse("social_media:post", kwargs={"slug": post_with_likes.slug}),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("likes_count") == 3  # noqa: PLR2004

    def test_post_detail_likes_count_field_type(self):
        """Test that likes_count field is returned as integer in detail view."""
        post = PostFactory(user=self.user)
        PostLikeFactory.create_batch(2, post=post)

        response = self.client.get(
            reverse("social_media:post", kwargs={"slug": post.slug}),
        )

        assert response.status_code == status.HTTP_200_OK
        likes_count = response.json().get("likes_count")
        assert isinstance(likes_count, int), "likes_count should be an integer"
        assert likes_count >= 0, "likes_count should not be negative"
        assert likes_count == 2  # noqa: PLR2004

    def test_post_detail_likes_count_consistency_after_update(self):
        """Test that likes_count remains consistent after post update."""
        post = PostFactory(user=self.user)
        PostLikeFactory.create_batch(2, post=post)

        # Update the post content
        response = self.client.put(
            reverse("social_media:post", kwargs={"slug": post.slug}),
            data={"content": "Updated content"},
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("content") == "Updated content"
        assert (
            response.json().get("likes_count") == 2  # noqa: PLR2004
        ), "likes_count should remain unchanged after update"
