from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from accounts.models import Follow
from accounts.models import Profile
from accounts.tests.factories import ProfileFactory
from core.users.tests.factories import UserFactory
from social_media.models import Post
from social_media.tests.factories import PostFactory


class TestPostPrivacyViews(TestCase):
    """Test cases for post privacy functionality."""

    def setUp(self):
        self.url = reverse("social-media:posts")

        # Create test users and profiles
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()

        self.profile1 = ProfileFactory(user=self.user1, profile_type=Profile.FARMER)
        self.profile2 = ProfileFactory(user=self.user2, profile_type=Profile.FARMER)
        self.profile3 = ProfileFactory(user=self.user3, profile_type=Profile.FARMER)

        # Make user1 and user2 friends (mutual followers)
        Follow.objects.create(follower=self.profile1, following=self.profile2)
        Follow.objects.create(follower=self.profile2, following=self.profile1)

        # User3 is not friends with anyone

    def test_create_post_with_default_privacy(self):
        """Test creating a post uses public privacy by default."""
        self.client.force_login(self.user1)

        response = self.client.post(
            self.url,
            {
                "content": "This is a test post",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        post_data = response.json()
        assert post_data["privacy"] == Post.PUBLIC

    def test_create_post_with_explicit_privacy(self):
        """Test creating posts with different privacy levels."""
        self.client.force_login(self.user1)

        # Test public post
        response = self.client.post(
            self.url,
            {
                "content": "Public post",
                "privacy": Post.PUBLIC,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["privacy"] == Post.PUBLIC

        # Test friends post
        response = self.client.post(
            self.url,
            {
                "content": "Friends post",
                "privacy": Post.FRIENDS,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["privacy"] == Post.FRIENDS

        # Test only me post
        response = self.client.post(
            self.url,
            {
                "content": "Only me post",
                "privacy": Post.ONLY_ME,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["privacy"] == Post.ONLY_ME

    def test_public_posts_visible_to_everyone(self):
        """Test that public posts are visible to all users."""
        # User1 creates a public post
        public_post = PostFactory(
            user=self.user1,
            privacy=Post.PUBLIC,
            content="Public post",
        )

        # Test authenticated users can see it
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert public_post.slug in post_slugs

        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert public_post.slug in post_slugs

        # Test unauthenticated users can see it
        self.client.logout()
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert public_post.slug in post_slugs

    def test_friends_posts_visible_to_friends_only(self):
        """Test that friends posts are only visible to friends and the author."""
        # User1 creates a friends post
        friends_post = PostFactory(
            user=self.user1,
            privacy=Post.FRIENDS,
            content="Friends post",
        )

        # User1 (author) can see it
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert friends_post.slug in post_slugs

        # User2 (friend) can see it
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert friends_post.slug in post_slugs

        # User3 (not friend) cannot see it
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert friends_post.slug not in post_slugs

        # Unauthenticated users cannot see it
        self.client.logout()
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert friends_post.slug not in post_slugs

    def test_only_me_posts_visible_to_author_only(self):
        """Test that only me posts are only visible to the author."""
        # User1 creates an only me post
        only_me_post = PostFactory(
            user=self.user1,
            privacy=Post.ONLY_ME,
            content="Only me post",
        )

        # User1 (author) can see it
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert only_me_post.slug in post_slugs

        # User2 (friend) cannot see it
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert only_me_post.slug not in post_slugs

        # User3 (not friend) cannot see it
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert only_me_post.slug not in post_slugs

        # Unauthenticated users cannot see it
        self.client.logout()
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert only_me_post.slug not in post_slugs

    def test_post_detail_privacy_filtering(self):
        """Test privacy filtering works for individual post retrieval."""
        # Create posts with different privacy levels
        public_post = PostFactory(user=self.user1, privacy=Post.PUBLIC)
        friends_post = PostFactory(user=self.user1, privacy=Post.FRIENDS)
        only_me_post = PostFactory(user=self.user1, privacy=Post.ONLY_ME)

        detail_url_public = reverse(
            "social-media:post-detail",
            kwargs={"slug": public_post.slug},
        )
        detail_url_friends = reverse(
            "social-media:post-detail",
            kwargs={"slug": friends_post.slug},
        )
        detail_url_only_me = reverse(
            "social-media:post-detail",
            kwargs={"slug": only_me_post.slug},
        )

        # Test as friend (user2)
        self.client.force_login(self.user2)

        # Can see public post
        response = self.client.get(detail_url_public)
        assert response.status_code == status.HTTP_200_OK

        # Can see friends post
        response = self.client.get(detail_url_friends)
        assert response.status_code == status.HTTP_200_OK

        # Cannot see only me post
        response = self.client.get(detail_url_only_me)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Test as non-friend (user3)
        self.client.force_login(self.user3)

        # Can see public post
        response = self.client.get(detail_url_public)
        assert response.status_code == status.HTTP_200_OK

        # Cannot see friends post
        response = self.client.get(detail_url_friends)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Cannot see only me post
        response = self.client.get(detail_url_only_me)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_post_privacy(self):
        """Test updating post privacy settings."""
        # User1 creates a public post
        post = PostFactory(user=self.user1, privacy=Post.PUBLIC, content="Test post")
        detail_url = reverse("social-media:post-detail", kwargs={"slug": post.slug})

        self.client.force_login(self.user1)

        # Update to friends only
        response = self.client.patch(
            detail_url,
            {
                "privacy": Post.FRIENDS,
            },
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["privacy"] == Post.FRIENDS

        # Verify the change took effect
        post.refresh_from_db()
        assert post.privacy == Post.FRIENDS

    def test_friendship_changes_affect_visibility(self):
        """Test that friendship changes affect post visibility."""
        # User1 creates a friends post
        friends_post = PostFactory(user=self.user1, privacy=Post.FRIENDS)

        # Initially user2 can see it (they are friends)
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert friends_post.slug in post_slugs

        # User1 unfollows user2 (they are no longer mutual friends)
        Follow.objects.filter(follower=self.profile1, following=self.profile2).delete()

        # Now user2 cannot see the friends post
        response = self.client.get(self.url)
        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert friends_post.slug not in post_slugs

    def test_privacy_field_in_serializer_responses(self):
        """Test that privacy field is included in all serializer responses."""
        # Create posts with different privacy levels
        PostFactory(user=self.user1, privacy=Post.PUBLIC)
        PostFactory(user=self.user1, privacy=Post.FRIENDS)
        PostFactory(user=self.user1, privacy=Post.ONLY_ME)

        self.client.force_login(self.user1)

        # Test post list
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        for post in response.json()["results"]:
            assert "privacy" in post
            assert post["privacy"] in [Post.PUBLIC, Post.FRIENDS, Post.ONLY_ME]

    def test_unauthenticated_user_only_sees_public_posts(self):
        """Test that unauthenticated users only see public posts."""
        # Create posts with different privacy levels
        public_post = PostFactory(user=self.user1, privacy=Post.PUBLIC)
        friends_post = PostFactory(user=self.user1, privacy=Post.FRIENDS)
        only_me_post = PostFactory(user=self.user1, privacy=Post.ONLY_ME)

        # Test as unauthenticated user
        self.client.logout()
        response = self.client.get(self.url)

        post_slugs = [p["slug"] for p in response.json()["results"]]
        assert public_post.slug in post_slugs
        assert friends_post.slug not in post_slugs
        assert only_me_post.slug not in post_slugs


class TestProfileFriendshipMethods(TestCase):
    """Test cases for Profile friendship helper methods."""

    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()

        self.profile1 = ProfileFactory(user=self.user1)
        self.profile2 = ProfileFactory(user=self.user2)
        self.profile3 = ProfileFactory(user=self.user3)

    def test_are_friends_when_mutual_followers(self):
        """Test are_friends returns True for mutual followers."""
        # Make them mutual followers
        Follow.objects.create(follower=self.profile1, following=self.profile2)
        Follow.objects.create(follower=self.profile2, following=self.profile1)

        assert self.profile1.are_friends(self.profile2)
        assert self.profile2.are_friends(self.profile1)

    def test_are_friends_when_one_way_follow(self):
        """Test are_friends returns False for one-way follows."""
        # Only one way follow
        Follow.objects.create(follower=self.profile1, following=self.profile2)

        assert not self.profile1.are_friends(self.profile2)
        assert not self.profile2.are_friends(self.profile1)

    def test_are_friends_when_no_relationship(self):
        """Test are_friends returns False when no relationship exists."""
        assert not self.profile1.are_friends(self.profile3)
        assert not self.profile3.are_friends(self.profile1)

    def test_are_friends_with_self(self):
        """Test are_friends returns False when checking with self."""
        assert not self.profile1.are_friends(self.profile1)
