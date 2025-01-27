from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from accounts.tests.factories import ProfileFactory
from social_media.tests.factories import PostFactory


class TestRetrieveUpdateDestroyPostView(TestCase):
    def setUp(self):
        self.url = reverse("social-media:post")
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

    def test_update_post(self):
        # Test that the user can update the post
        response = self.client.put(
            reverse("social_media:post", kwargs={"slug": self.posts[0].slug}),
            data={"content": "New content"},
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("content") == "New content"

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
