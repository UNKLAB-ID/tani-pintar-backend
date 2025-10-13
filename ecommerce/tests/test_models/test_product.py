import pytest
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from core.users.tests.factories import UserFactory
from ecommerce.models import Product
from ecommerce.tests.factories import ProductCategoryFactory
from ecommerce.tests.factories import ProductFactory
from ecommerce.tests.factories import ProductImageFactory
from ecommerce.tests.factories import ProductPriceFactory


class ProductModelTest(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        """Set up test data for Product model tests."""
        self.product = ProductFactory(
            name="Test Product",
            description="Test product description",
            available_stock=100,
        )
        self.user = self.product.user
        self.category = self.product.category

    def test_product_creation(self):
        """Test that Product can be created successfully."""
        assert self.product.name == "Test Product"
        assert self.product.description == "Test product description"
        assert self.product.available_stock == 100  # noqa: PLR2004
        assert self.product.user == self.user
        assert self.product.category == self.category
        assert self.product.status == Product.STATUS_ACTIVE
        assert self.product.approval_status == Product.APPROVAL_APPROVED
        assert self.product.created_at is not None
        assert self.product.updated_at is not None

    def test_product_str_representation(self):
        """Test the string representation of Product."""
        assert str(self.product) == "Test Product"

    def test_product_slug_auto_generation(self):
        """Test that slug is automatically generated from name."""
        product = ProductFactory(
            user=self.user,
            category=self.category,
            name="Amazing Product Name",
        )
        expected_slug = slugify("Amazing Product Name")
        assert product.slug == expected_slug

    def test_product_slug_uniqueness(self):
        """Test that duplicate product names generate unique slugs."""
        product1 = ProductFactory(
            user=self.user,
            category=self.category,
            name="Duplicate Name",
        )
        product2 = ProductFactory(
            user=self.user,
            category=self.category,
            name="Duplicate Name",
        )

        assert product1.slug != product2.slug
        assert product1.slug == slugify("Duplicate Name")
        assert product2.slug == f"{slugify('Duplicate Name')}-1"

    def test_product_slug_must_be_unique(self):
        """Test that slug field has unique constraint."""
        product1 = ProductFactory(
            user=self.user,
            category=self.category,
        )

        # Attempt to create another product with the same slug should fail
        with pytest.raises(IntegrityError):
            Product.objects.create(
                user=self.user,
                category=self.category,
                name="Different Name",
                slug=product1.slug,
                description="Test description",
                image="test.jpg",
            )

    def test_product_status_choices(self):
        """Test that all status choices are valid."""
        # Test draft status
        draft_product = ProductFactory(
            user=self.user,
            category=self.category,
            status=Product.STATUS_DRAFT,
        )
        assert draft_product.status == Product.STATUS_DRAFT

        # Test active status
        active_product = ProductFactory(
            user=self.user,
            category=self.category,
            status=Product.STATUS_ACTIVE,
        )
        assert active_product.status == Product.STATUS_ACTIVE

        # Test inactive status
        inactive_product = ProductFactory(
            user=self.user,
            category=self.category,
            status=Product.STATUS_INACTIVE,
        )
        assert inactive_product.status == Product.STATUS_INACTIVE

    def test_product_approval_status_choices(self):
        """Test that all approval status choices are valid."""
        # Test pending approval
        pending_product = ProductFactory(
            user=self.user,
            category=self.category,
            approval_status=Product.APPROVAL_PENDING,
        )
        assert pending_product.approval_status == Product.APPROVAL_PENDING

        # Test approved
        approved_product = ProductFactory(
            user=self.user,
            category=self.category,
            approval_status=Product.APPROVAL_APPROVED,
        )
        assert approved_product.approval_status == Product.APPROVAL_APPROVED

        # Test rejected
        rejected_product = ProductFactory(
            user=self.user,
            category=self.category,
            approval_status=Product.APPROVAL_REJECTED,
        )
        assert rejected_product.approval_status == Product.APPROVAL_REJECTED

    def test_product_default_status(self):
        """Test that default status is DRAFT."""
        user = UserFactory()
        category = ProductCategoryFactory()
        product = Product.objects.create(
            user=user,
            category=category,
            name="Test Product",
            description="Test description",
            image="test.jpg",
        )
        assert product.status == Product.STATUS_DRAFT

    def test_product_default_approval_status(self):
        """Test that default approval status is PENDING."""
        user = UserFactory()
        category = ProductCategoryFactory()
        product = Product.objects.create(
            user=user,
            category=category,
            name="Test Product",
            description="Test description",
            image="test.jpg",
        )
        assert product.approval_status == Product.APPROVAL_PENDING

    def test_product_default_available_stock(self):
        """Test that default available stock is 0."""
        user = UserFactory()
        category = ProductCategoryFactory()
        product = Product.objects.create(
            user=user,
            category=category,
            name="Test Product",
            description="Test description",
            image="test.jpg",
        )
        assert product.available_stock == 0

    def test_product_uuid_field(self):
        """Test that uuid is auto-generated and is primary key."""
        assert self.product.uuid is not None
        assert str(self.product.uuid) != ""
        # UUID should be unique
        product2 = ProductFactory(user=self.user, category=self.category)
        assert self.product.uuid != product2.uuid

    def test_product_user_relationship(self):
        """Test that product correctly relates to user."""
        assert self.product.user == self.user
        # Check reverse relationship
        assert self.product in self.user.products.all()

    def test_product_category_relationship(self):
        """Test that product correctly relates to category."""
        assert self.product.category == self.category
        # Check reverse relationship
        assert self.product in self.category.products.all()

    def test_cascade_delete_user(self):
        """Test that deleting a user also deletes related products."""
        product_uuid = self.product.uuid
        self.user.delete()
        assert not Product.objects.filter(uuid=product_uuid).exists()

    def test_cascade_delete_category(self):
        """Test that deleting a category also deletes related products."""
        product_uuid = self.product.uuid
        self.category.delete()
        assert not Product.objects.filter(uuid=product_uuid).exists()

    def test_product_images_relationship(self):
        """Test that product can have multiple images."""
        # Get initial count from factory
        initial_count = self.product.images.count()

        # Add 3 more images
        ProductImageFactory(product=self.product)
        ProductImageFactory(product=self.product)
        ProductImageFactory(product=self.product)

        # Check that count increased by 3
        assert self.product.images.count() == initial_count + 3

    def test_product_prices_relationship(self):
        """Test that product can have multiple prices."""
        # Get initial count from factory
        initial_count = self.product.prices.count()

        # Add 2 more prices
        ProductPriceFactory(product=self.product)
        ProductPriceFactory(product=self.product)

        # Check that count increased by 2
        assert self.product.prices.count() == initial_count + 2

    def test_product_ordering(self):
        """Test that products are ordered by created_at descending."""
        product1 = ProductFactory(
            user=self.user,
            category=self.category,
            name="Product 1",
        )
        product2 = ProductFactory(
            user=self.user,
            category=self.category,
            name="Product 2",
        )
        product3 = ProductFactory(
            user=self.user,
            category=self.category,
            name="Product 3",
        )

        products = Product.objects.all()
        # Most recent first
        assert products[0] == product3
        assert products[1] == product2
        assert products[2] == product1

    def test_product_with_zero_stock(self):
        """Test that product can have zero stock."""
        product = ProductFactory(
            user=self.user,
            category=self.category,
            available_stock=0,
        )
        assert product.available_stock == 0

    def test_product_with_high_stock(self):
        """Test that product can have high stock value."""
        product = ProductFactory(
            user=self.user,
            category=self.category,
            available_stock=999999,
        )
        assert product.available_stock == 999999  # noqa: PLR2004

    def test_product_timestamps(self):
        """Test that created_at and updated_at are set correctly."""
        assert self.product.created_at is not None
        assert self.product.updated_at is not None
        assert self.product.created_at <= self.product.updated_at

    def test_product_history_tracking(self):
        """Test that product changes are tracked in history."""
        original_name = self.product.name
        self.product.name = "Updated Product Name"
        self.product.save()

        # Check that history was created
        history = self.product.history.all()
        assert history.count() >= 2  # noqa: PLR2004
        # Most recent history should have updated name
        assert history[0].name == "Updated Product Name"
        # Older history should have original name
        assert history[1].name == original_name

    def test_multiple_products_same_user(self):
        """Test that a user can have multiple products."""
        ProductFactory(user=self.user, category=self.category)
        ProductFactory(user=self.user, category=self.category)
        ProductFactory(user=self.user, category=self.category)

        assert (
            self.user.products.count() >= 4  # noqa: PLR2004
        )  # Including setUp product

    def test_multiple_products_same_category(self):
        """Test that a category can have multiple products."""
        ProductFactory(user=self.user, category=self.category)
        ProductFactory(user=self.user, category=self.category)
        ProductFactory(user=self.user, category=self.category)

        assert (
            self.category.products.count() >= 4  # noqa: PLR2004
        )  # Including setUp product

    def test_product_with_long_description(self):
        """Test that product can have long description."""
        long_description = "A" * 5000  # 5000 characters
        product = ProductFactory(
            user=self.user,
            category=self.category,
            description=long_description,
        )
        assert len(product.description) == 5000  # noqa: PLR2004

    def test_product_meta_verbose_names(self):
        """Test that model meta verbose names are correct."""
        assert Product._meta.verbose_name == "Product"  # noqa: SLF001
        assert Product._meta.verbose_name_plural == "Products"  # noqa: SLF001

    def test_product_required_fields(self):
        """Test that required fields cannot be null."""
        with pytest.raises(  # noqa: B017
            Exception,  # noqa: PT011
        ):  # Can be IntegrityError or ValidationError
            Product.objects.create(
                # Missing required fields
                description="Test",
            )

    def test_product_update_preserves_slug(self):
        """Test that updating product doesn't change existing slug."""
        original_slug = self.product.slug
        self.product.name = "Completely Different Name"
        self.product.save()

        # Slug should remain the same
        assert self.product.slug == original_slug

    def test_product_factory_with_images_generation(self):
        """Test that ProductFactory can generate images."""
        product = ProductFactory(images=3)
        assert product.images.count() == 3  # noqa: PLR2004

    def test_product_factory_with_prices_generation(self):
        """Test that ProductFactory can generate prices."""
        product = ProductFactory(prices=2)
        assert product.prices.count() == 2  # noqa: PLR2004
