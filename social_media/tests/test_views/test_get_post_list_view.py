from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.users.tests.factories import UserFactory
from social_media.tests.factories import PostFactory


class TestGetPostListView(TestCase):
    def setUp(self):
        self.url = reverse("social-media:post")
        self.user = UserFactory()
        self.posts = PostFactory.create_batch(25)
        self.client.force_login(self.user)

    def test_get_post_list(self):
        response = self.client.get(self.url)
        posts = response.json()
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert len(posts.get("results")) == 15, "Should return 15 posts"  # noqa: PLR2004
        for post in posts.get("results"):
            assert len(post.get("images")) == 3, "Each post should contain 3 images"  # noqa: PLR2004
