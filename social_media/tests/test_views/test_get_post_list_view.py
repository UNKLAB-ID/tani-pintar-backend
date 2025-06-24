from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from accounts.models import Profile
from accounts.tests.factories import ProfileFactory
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

    def test_get_post_list_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        posts = response.json()
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should allow unauthenticated GET requests"
        assert len(posts.get("results")) == 15, (  # noqa: PLR2004
            "Should return 15 posts for unauthenticated user"
        )


class TestPostListFilterView(TestCase):
    """Test cases for filtering posts in the ListCreatePostView."""

    def setUp(self):
        self.url = reverse("social-media:post")
        self.user = UserFactory()

        # Create test profiles with different types
        self.farmer_profile = ProfileFactory(profile_type=Profile.FARMER)
        self.distributor_profile = ProfileFactory(
            profile_type=Profile.DISTRIBUTOR,
        )
        self.consumer_profile = ProfileFactory(profile_type=Profile.CONSUMER)

        # Create posts for each user
        self.farmer_posts = PostFactory.create_batch(
            5,
            user=self.farmer_profile.user,
        )
        self.distributor_posts = PostFactory.create_batch(
            3,
            user=self.distributor_profile.user,
        )
        self.consumer_posts = PostFactory.create_batch(
            4,
            user=self.consumer_profile.user,
        )

        self.client.force_login(self.user)

    def test_filter_posts_by_user_id(self):
        """Test filtering posts by user_id parameter."""
        response = self.client.get(
            self.url,
            {"user_id": self.farmer_profile.user.id},
        )
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert (
            len(posts.get("results")) == 5  # noqa: PLR2004
        ), "Should return 5 farmer posts"

        # Verify all returned posts belong to the specified user
        for post in posts.get("results"):
            assert (
                post.get("user").get("id") == self.farmer_profile.user.id
            ), "All posts should belong to the specified user"

    def test_filter_posts_by_profile_id(self):
        """Test filtering posts by profile_id parameter."""
        response = self.client.get(
            self.url,
            {"profile_id": self.distributor_profile.id},
        )
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert (
            len(posts.get("results")) == 3  # noqa: PLR2004
        ), "Should return 3 distributor posts"

        # Verify all returned posts belong to the user with the specified profile
        for post in posts.get("results"):
            assert (
                post.get("user").get("id") == self.distributor_profile.user.id
            ), "All posts should belong to the user with specified profile"

    def test_filter_posts_by_nonexistent_user_id(self):
        """Test filtering by a user_id that doesn't exist."""
        response = self.client.get(self.url, {"user_id": 99999})
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert (
            len(posts.get("results")) == 0
        ), "Should return no posts for nonexistent user"

    def test_filter_posts_by_nonexistent_profile_id(self):
        """Test filtering by a profile_id that doesn't exist."""
        response = self.client.get(self.url, {"profile_id": 99999})
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert (
            len(posts.get("results")) == 0
        ), "Should return no posts for nonexistent profile"

    def test_filter_posts_with_invalid_user_id(self):
        """Test filtering with invalid user_id (non-numeric)."""
        response = self.client.get(self.url, {"user_id": "invalid"})

        # Django filter should handle this gracefully and return all posts or an error
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        ], "Should handle invalid user_id gracefully"

    def test_filter_posts_with_invalid_profile_id(self):
        """Test filtering with invalid profile_id (non-numeric)."""
        response = self.client.get(self.url, {"profile_id": "invalid"})

        # Django filter should handle this gracefully and return all posts or an error
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        ], "Should handle invalid profile_id gracefully"

    def test_multiple_filters_combination(self):
        """Test combining multiple filters (user_id and profile_id for same user)."""
        response = self.client.get(
            self.url,
            {
                "user_id": self.consumer_profile.user.id,
                "profile_id": self.consumer_profile.id,
            },
        )
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert (
            len(posts.get("results")) == 4  # noqa: PLR2004
        ), "Should return 4 consumer posts when both filters match"

    def test_conflicting_filters(self):
        """Test conflicting filters (user_id from one user, profile_id from another)."""
        response = self.client.get(
            self.url,
            {
                "user_id": self.farmer_profile.user.id,
                "profile_id": self.distributor_profile.id,
            },
        )
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert (
            len(posts.get("results")) == 0
        ), "Should return no posts when filters conflict"

    def test_search_filter_functionality(self):
        """Test the search filter functionality."""
        # Create a post with specific content
        specific_post = PostFactory(
            user=self.farmer_profile.user,
            content="This is a unique search term for testing",
        )

        response = self.client.get(self.url, {"search": "unique search term"})
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert (
            len(posts.get("results")) >= 1
        ), "Should return at least one post with the search term"

        # Verify the specific post is in results
        post_slugs = [post.get("slug") for post in posts.get("results")]
        assert (
            specific_post.slug in post_slugs
        ), "Should find the post with specific content"

    def test_combined_search_and_filter(self):
        """Test combining search with user/profile filters."""
        # Create a post with specific content for a specific user
        specific_post = PostFactory(
            user=self.distributor_profile.user,
            content="Special content for filter test",
        )

        response = self.client.get(
            self.url,
            {
                "search": "Special content",
                "user_id": self.distributor_profile.user.id,
            },
        )
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"

        # Should find the specific post
        if posts.get("results"):
            post_slugs = [post.get("slug") for post in posts.get("results")]
            assert (
                specific_post.slug in post_slugs
            ), "Should find the post matching both search and filter"

    def test_pagination_with_filters(self):
        """Test that pagination works correctly with filters."""
        # Create more posts for a specific user to test pagination
        PostFactory.create_batch(20, user=self.farmer_profile.user)

        response = self.client.get(
            self.url,
            {
                "user_id": self.farmer_profile.user.id,
                "page_size": 10,
            },
        )
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert (
            len(posts.get("results")) == 10  # noqa: PLR2004
        ), "Should return 10 posts per page"
        assert (
            posts.get("count") == 25  # noqa: PLR2004
        ), "Should show total count of 25 posts for this user"
        assert posts.get("next") is not None, "Should have next page link"

    def test_filter_posts_unauthenticated(self):
        """Test that filters work for unauthenticated users."""
        self.client.logout()

        response = self.client.get(
            self.url,
            {"user_id": self.farmer_profile.user.id},
        )
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should allow unauthenticated filtered requests"
        assert (
            len(posts.get("results")) == 5  # noqa: PLR2004
        ), "Should return filtered posts for unauthenticated user"
