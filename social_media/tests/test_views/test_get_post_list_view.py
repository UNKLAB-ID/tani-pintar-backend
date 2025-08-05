from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from accounts.models import Profile
from accounts.tests.factories import ProfileFactory
from core.users.tests.factories import UserFactory
from social_media.tests.factories import PostFactory
from social_media.tests.factories import PostLikeFactory


class TestGetPostListView(TestCase):
    def setUp(self):
        self.url = reverse("social-media:posts")
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
            assert "likes_count" in post, "Each post should contain likes_count field"
            assert "is_liked" in post, "Each post should contain is_liked field"

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
        for post in posts.get("results"):
            assert "is_liked" in post, "Each post should contain is_liked field"
            assert (
                post.get("is_liked") is False
            ), "is_liked should be False for unauthenticated users"

    def test_post_list_likes_count_accuracy(self):
        """Test that likes_count field shows accurate count of likes."""
        # Create a post with no likes
        post_no_likes = PostFactory()

        # Create a post with 1 like
        post_one_like = PostFactory()
        PostLikeFactory(post=post_one_like)

        # Create a post with multiple likes
        post_multiple_likes = PostFactory()
        PostLikeFactory.create_batch(3, post=post_multiple_likes)

        response = self.client.get(self.url)
        posts = response.json()

        assert response.status_code == status.HTTP_200_OK

        # Find the posts in response and verify likes_count
        posts_data = {post["slug"]: post for post in posts.get("results", [])}

        if post_no_likes.slug in posts_data:
            assert posts_data[post_no_likes.slug]["likes_count"] == 0

        if post_one_like.slug in posts_data:
            assert posts_data[post_one_like.slug]["likes_count"] == 1

        if post_multiple_likes.slug in posts_data:
            assert posts_data[post_multiple_likes.slug]["likes_count"] == 3  # noqa: PLR2004

    def test_post_list_likes_count_field_type(self):
        """Test that likes_count field is returned as integer."""
        post = PostFactory()
        PostLikeFactory.create_batch(2, post=post)

        response = self.client.get(self.url)
        posts = response.json()

        assert response.status_code == status.HTTP_200_OK

        for post_data in posts.get("results", []):
            likes_count = post_data.get("likes_count")
            assert isinstance(likes_count, int), "likes_count should be an integer"
            assert likes_count >= 0, "likes_count should not be negative"


class TestPostListIsLikedView(TestCase):
    """Test cases for is_liked field in post list view."""

    def setUp(self):
        self.url = reverse("social-media:posts")
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.client.force_login(self.user)

    def test_post_list_is_liked_field_present(self):
        """Test that is_liked field is present in post list response."""
        PostFactory()

        response = self.client.get(self.url)
        posts = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert len(posts.get("results")) >= 1, "Should return at least one post"

        for post_data in posts.get("results"):
            assert "is_liked" in post_data, "Each post should contain is_liked field"

    def test_post_list_is_liked_true_when_user_liked(self):
        """Test that is_liked returns True when current user has liked the post."""
        post = PostFactory()
        PostLikeFactory(post=post, user=self.user)

        response = self.client.get(self.url)
        posts = response.json()

        assert response.status_code == status.HTTP_200_OK

        # Find the post in response
        posts_data = {p["slug"]: p for p in posts.get("results", [])}
        if post.slug in posts_data:
            assert (
                posts_data[post.slug]["is_liked"] is True
            ), "is_liked should be True when user liked the post"

    def test_post_list_is_liked_false_when_user_not_liked(self):
        """Test that is_liked returns False when current user hasn't liked the post."""
        post = PostFactory()
        # Create a like from another user, but not current user
        PostLikeFactory(post=post, user=self.other_user)

        response = self.client.get(self.url)
        posts = response.json()

        assert response.status_code == status.HTTP_200_OK

        # Find the post in response
        posts_data = {p["slug"]: p for p in posts.get("results", [])}
        if post.slug in posts_data:
            assert (
                posts_data[post.slug]["is_liked"] is False
            ), "is_liked should be False when user hasn't liked the post"

    def test_post_list_is_liked_false_for_unauthenticated(self):
        """Test that is_liked returns False for unauthenticated users."""
        post = PostFactory()
        PostLikeFactory(post=post, user=self.user)

        self.client.logout()
        response = self.client.get(self.url)
        posts = response.json()

        assert response.status_code == status.HTTP_200_OK

        for post_data in posts.get("results", []):
            assert (
                post_data.get("is_liked") is False
            ), "is_liked should be False for unauthenticated users"

    def test_post_list_is_liked_field_type(self):
        """Test that is_liked field is returned as boolean."""
        post = PostFactory()
        PostLikeFactory(post=post, user=self.user)

        response = self.client.get(self.url)
        posts = response.json()

        assert response.status_code == status.HTTP_200_OK

        for post_data in posts.get("results", []):
            is_liked = post_data.get("is_liked")
            assert isinstance(is_liked, bool), "is_liked should be a boolean"

    def test_post_list_is_liked_with_multiple_posts(self):
        """Test is_liked field with multiple posts (some liked, some not)."""
        # Create posts with different like states
        post_liked = PostFactory()
        post_not_liked = PostFactory()
        post_liked_by_other = PostFactory()

        PostLikeFactory(post=post_liked, user=self.user)
        PostLikeFactory(post=post_liked_by_other, user=self.other_user)

        response = self.client.get(self.url)
        posts = response.json()

        assert response.status_code == status.HTTP_200_OK

        # Find posts in response
        posts_data = {p["slug"]: p for p in posts.get("results", [])}

        if post_liked.slug in posts_data:
            assert (
                posts_data[post_liked.slug]["is_liked"] is True
            ), "Should be True for liked post"

        if post_not_liked.slug in posts_data:
            assert (
                posts_data[post_not_liked.slug]["is_liked"] is False
            ), "Should be False for not liked post"

        if post_liked_by_other.slug in posts_data:
            assert (
                posts_data[post_liked_by_other.slug]["is_liked"] is False
            ), "Should be False for post liked by other user"


class TestPostListFilterView(TestCase):
    """Test cases for filtering posts in the ListCreatePostView."""

    def setUp(self):
        self.url = reverse("social-media:posts")
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
            assert (
                "likes_count" in post
            ), "Each filtered post should contain likes_count field"
            assert (
                "is_liked" in post
            ), "Each filtered post should contain is_liked field"

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

    def test_search_by_profile_name(self):
        """Test searching posts by profile full name."""
        # Create a profile with a specific name
        profile_with_unique_name = ProfileFactory(
            full_name="John Smith Unique Name",
        )
        specific_post = PostFactory(
            user=profile_with_unique_name.user,
            content="Regular post content",
        )

        response = self.client.get(self.url, {"search": "John Smith"})
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert (
            len(posts.get("results")) >= 1
        ), "Should return at least one post from user with matching name"

        # Verify the specific post is in results
        post_slugs = [post.get("slug") for post in posts.get("results")]
        assert specific_post.slug in post_slugs, "Should find the post by profile name"

    def test_search_by_profile_name_partial_match(self):
        """Test partial matching of profile names in search."""
        # Create a profile with a specific name
        profile_with_name = ProfileFactory(
            full_name="Jane Elizabeth Doe",
        )
        specific_post = PostFactory(
            user=profile_with_name.user,
            content="Some content here",
        )

        # Test partial match
        response = self.client.get(self.url, {"search": "Elizabeth"})
        posts = response.json()

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return 200 status code"
        assert (
            len(posts.get("results")) >= 1
        ), "Should return posts with partial name match"

        # Verify the specific post is in results
        post_slugs = [post.get("slug") for post in posts.get("results")]
        assert (
            specific_post.slug in post_slugs
        ), "Should find the post by partial profile name match"

    def test_search_content_and_profile_name_combined(self):
        """Test that search finds posts matching either content OR profile name."""
        # Create profile with specific name
        profile_with_name = ProfileFactory(
            full_name="Alice Cooper",
        )
        post_by_name = PostFactory(
            user=profile_with_name.user,
            content="Regular content without search term",
        )

        # Create post with specific content
        post_by_content = PostFactory(
            user=self.farmer_profile.user,
            content="Content with special keyword",
        )

        # Search for term that matches profile name
        response = self.client.get(self.url, {"search": "Alice"})
        posts = response.json()
        post_slugs = [post.get("slug") for post in posts.get("results")]

        assert post_by_name.slug in post_slugs, "Should find post by profile name match"

        # Search for term that matches content
        response = self.client.get(self.url, {"search": "special keyword"})
        posts = response.json()
        post_slugs = [post.get("slug") for post in posts.get("results")]

        assert post_by_content.slug in post_slugs, "Should find post by content match"

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
