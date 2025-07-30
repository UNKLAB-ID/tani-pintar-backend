import pytest
from django.db import IntegrityError
from django.test import TestCase

from core.users.tests.factories import UserFactory
from social_media.models import PostCommentLike
from social_media.tests.factories import PostCommentFactory
from social_media.tests.factories import PostCommentLikeFactory


class PostCommentLikeModelTest(TestCase):
    """
    Test suite for PostCommentLike model functionality.

    Tests model creation, validation, constraints, relationships,
    and string representation. Ensures the model behaves correctly
    in various scenarios including edge cases.
    """

    def setUp(self):
        """Set up test data for PostCommentLike model tests."""
        self.user = UserFactory()
        self.comment = PostCommentFactory()

    def test_post_comment_like_creation(self):
        """Test successful creation of PostCommentLike instance."""
        like = PostCommentLike.objects.create(
            comment=self.comment,
            user=self.user,
        )

        assert like.comment == self.comment
        assert like.user == self.user
        assert like.created_at is not None
        assert isinstance(like.id, int)

    def test_post_comment_like_str_representation(self):
        """Test string representation of PostCommentLike model."""
        like = PostCommentLikeFactory(comment=self.comment, user=self.user)
        expected_str = f"User {self.user.username} liked Comment {self.comment.id}"

        assert str(like) == expected_str

    def test_unique_constraint_comment_user(self):
        """Test that unique constraint prevents duplicate likes on same comment by same user."""  # noqa: E501
        # Create first like
        PostCommentLike.objects.create(comment=self.comment, user=self.user)

        # Attempt to create duplicate like should raise IntegrityError
        with pytest.raises(IntegrityError):
            PostCommentLike.objects.create(comment=self.comment, user=self.user)

    def test_different_users_can_like_same_comment(self):
        """Test that different users can like the same comment."""
        user1 = UserFactory()
        user2 = UserFactory()

        like1 = PostCommentLike.objects.create(comment=self.comment, user=user1)
        like2 = PostCommentLike.objects.create(comment=self.comment, user=user2)

        assert like1.comment == like2.comment
        assert like1.user != like2.user
        assert PostCommentLike.objects.filter(comment=self.comment).count() == 2  # noqa: PLR2004

    def test_same_user_can_like_different_comments(self):
        """Test that same user can like multiple different comments."""
        comment1 = PostCommentFactory()
        comment2 = PostCommentFactory()

        like1 = PostCommentLike.objects.create(comment=comment1, user=self.user)
        like2 = PostCommentLike.objects.create(comment=comment2, user=self.user)

        assert like1.user == like2.user
        assert like1.comment != like2.comment
        assert PostCommentLike.objects.filter(user=self.user).count() == 2  # noqa: PLR2004

    def test_cascade_delete_on_comment_deletion(self):
        """Test that PostCommentLike is deleted when associated comment is deleted."""
        like = PostCommentLikeFactory(comment=self.comment)
        like_id = like.id

        # Delete the comment
        self.comment.delete()

        # Verify like is also deleted
        assert not PostCommentLike.objects.filter(id=like_id).exists()

    def test_cascade_delete_on_user_deletion(self):
        """Test that PostCommentLike is deleted when associated user is deleted."""
        like = PostCommentLikeFactory(user=self.user)
        like_id = like.id

        # Delete the user
        self.user.delete()

        # Verify like is also deleted
        assert not PostCommentLike.objects.filter(id=like_id).exists()

    def test_related_name_likes_on_comment(self):
        """Test that related_name 'likes' works correctly on PostComment."""
        like1 = PostCommentLikeFactory(comment=self.comment)
        like2 = PostCommentLikeFactory(comment=self.comment)

        comment_likes = self.comment.likes.all()
        assert comment_likes.count() == 2  # noqa: PLR2004
        assert like1 in comment_likes
        assert like2 in comment_likes

    def test_comment_like_foreign_key_relationships(self):
        """Test foreign key relationships are properly established."""
        like = PostCommentLikeFactory(comment=self.comment, user=self.user)

        # Test forward relationships
        assert like.comment == self.comment
        assert like.user == self.user

        # Test reverse relationship
        assert like in self.comment.likes.all()

    def test_factory_creates_valid_instance(self):
        """Test that PostCommentLikeFactory creates valid instances."""
        like = PostCommentLikeFactory()

        assert isinstance(like, PostCommentLike)
        assert like.comment is not None
        assert like.user is not None
        assert like.created_at is not None

    def test_factory_with_custom_attributes(self):
        """Test PostCommentLikeFactory with custom attributes."""
        custom_comment = PostCommentFactory()
        custom_user = UserFactory()

        like = PostCommentLikeFactory(comment=custom_comment, user=custom_user)

        assert like.comment == custom_comment
        assert like.user == custom_user

    def test_multiple_likes_ordering(self):
        """Test that multiple likes are properly ordered by creation time."""
        like1 = PostCommentLikeFactory(comment=self.comment)
        like2 = PostCommentLikeFactory(comment=self.comment)
        like3 = PostCommentLikeFactory(comment=self.comment)

        likes = PostCommentLike.objects.filter(comment=self.comment).order_by(
            "created_at",
        )

        assert list(likes) == [like1, like2, like3]

    def test_unique_constraint_name(self):
        """Test that the unique constraint has the correct name."""
        like = PostCommentLikeFactory()
        meta = like._meta  # noqa: SLF001

        constraint_names = [constraint.name for constraint in meta.constraints]
        assert "unique_comment_like" in constraint_names

    def test_model_fields_configuration(self):
        """Test that model fields are configured correctly."""
        like = PostCommentLikeFactory()

        # Test comment field
        comment_field = like._meta.get_field("comment")  # noqa: SLF001
        assert comment_field.related_model.__name__ == "PostComment"
        assert comment_field.remote_field.on_delete.__name__ == "CASCADE"
        assert comment_field.remote_field.related_name == "likes"

        # Test user field
        user_field = like._meta.get_field("user")  # noqa: SLF001
        assert user_field.related_model.__name__ == "User"
        assert user_field.remote_field.on_delete.__name__ == "CASCADE"

        # Test created_at field
        created_at_field = like._meta.get_field("created_at")  # noqa: SLF001
        assert created_at_field.auto_now_add is True
