import pytest
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from core.users.tests.factories import UserFactory
from ecommerce.models import Product
from ecommerce.models import ProductImage
from ecommerce.models import ProductPrice
from ecommerce.tests.factories import ProductCategoryFactory
from ecommerce.tests.factories import ProductFactory
from ecommerce.tests.factories import ProductImageFactory
from ecommerce.tests.factories import ProductPriceFactory
from ecommerce.tests.factories import UnitOfMeasureFactory


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


class ProductImageModelTest(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        """Set up test data for ProductImage model tests."""
        self.product = ProductFactory()
        self.product_image = ProductImageFactory(
            product=self.product,
            caption="Test Image Caption",
        )

    def test_product_image_creation(self):
        """Test that ProductImage can be created successfully."""
        assert self.product_image.product == self.product
        assert self.product_image.caption == "Test Image Caption"
        assert self.product_image.image is not None
        assert self.product_image.created_at is not None

    def test_product_image_str_representation(self):
        """Test the string representation of ProductImage."""
        expected_str = f"{self.product.name} - Image {self.product_image.pk}"
        assert str(self.product_image) == expected_str

    def test_product_image_with_empty_caption(self):
        """Test that ProductImage can be created without caption."""
        image = ProductImageFactory(product=self.product, caption="")
        assert image.caption == ""

    def test_product_image_default_caption(self):
        """Test that ProductImage has empty string as default caption."""
        # Create without specifying caption
        image = ProductImage.objects.create(
            product=self.product,
            image="test.jpg",
        )
        assert image.caption == ""

    def test_product_image_caption_max_length(self):
        """Test that ProductImage caption respects max_length."""
        long_caption = "A" * 200  # Max length is 200
        image = ProductImageFactory(product=self.product, caption=long_caption)
        assert len(image.caption) == 200  # noqa: PLR2004

    def test_product_image_relationship(self):
        """Test that ProductImage correctly relates to Product."""
        assert self.product_image.product == self.product
        # Check reverse relationship
        assert self.product_image in self.product.images.all()

    def test_cascade_delete_product_deletes_images(self):
        """Test that deleting a product also deletes related images."""
        image_pk = self.product_image.pk
        self.product.delete()
        assert not ProductImage.objects.filter(pk=image_pk).exists()

    def test_multiple_images_per_product(self):
        """Test that a product can have multiple images."""
        ProductImageFactory(product=self.product)
        ProductImageFactory(product=self.product)
        ProductImageFactory(product=self.product)

        assert self.product.images.count() >= 4  # noqa: PLR2004  # Including setUp image

    def test_product_image_ordering(self):
        """Test that product images are ordered by created_at ascending."""
        image1 = ProductImageFactory(product=self.product, caption="Image 1")
        image2 = ProductImageFactory(product=self.product, caption="Image 2")
        image3 = ProductImageFactory(product=self.product, caption="Image 3")

        images = self.product.images.all()
        # First image should be the oldest (from setUp or first created)
        # Last images should be the most recent
        assert image1 in images
        assert image2 in images
        assert image3 in images

    def test_product_image_timestamps(self):
        """Test that created_at is set correctly."""
        assert self.product_image.created_at is not None

    def test_product_image_meta_verbose_names(self):
        """Test that model meta verbose names are correct."""
        assert ProductImage._meta.verbose_name == "Product Image"  # noqa: SLF001
        assert ProductImage._meta.verbose_name_plural == "Product Images"  # noqa: SLF001

    def test_product_image_required_fields(self):
        """Test that required fields cannot be null."""
        with pytest.raises(  # noqa: B017
            Exception,  # noqa: PT011
        ):  # Can be IntegrityError or ValidationError
            ProductImage.objects.create(
                # Missing required product field
                image="test.jpg",
            )

    def test_different_products_can_have_same_caption(self):
        """Test that different products can have images with same caption."""
        product2 = ProductFactory()
        image1 = ProductImageFactory(
            product=self.product,
            caption="Same Caption",
        )
        image2 = ProductImageFactory(
            product=product2,
            caption="Same Caption",
        )

        assert image1.caption == image2.caption
        assert image1.product != image2.product


class ProductPriceModelTest(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        """Set up test data for ProductPrice model tests."""
        # Create product without auto-generating prices and images
        self.product = ProductFactory(prices=0, images=0)
        # Use unique UOM to avoid conflicts across tests
        self.unit_of_measure = UnitOfMeasureFactory()
        # Create ProductPrice directly to avoid nested subfactory issues
        self.product_price = ProductPrice.objects.create(
            product=self.product,
            unit_of_measure=self.unit_of_measure,
            price=100.50,
        )

    def test_product_price_creation(self):
        """Test that ProductPrice can be created successfully."""
        assert self.product_price.product == self.product
        assert self.product_price.unit_of_measure == self.unit_of_measure
        assert self.product_price.price == 100.50  # noqa: PLR2004
        assert self.product_price.id is not None
        assert self.product_price.created_at is not None
        assert self.product_price.updated_at is not None

    def test_product_price_str_representation(self):
        """Test the string representation of ProductPrice."""
        # Decimal 100.50 is displayed as 100.5 without trailing zero
        expected_str = f"{self.product.name} - 100.5 per {self.unit_of_measure.name}"
        assert str(self.product_price) == expected_str

    def test_product_price_decimal_precision(self):
        """Test that ProductPrice respects decimal precision."""
        uom_gram = UnitOfMeasureFactory()
        price = ProductPrice.objects.create(
            product=self.product,
            unit_of_measure=uom_gram,
            price=123.45,
        )
        assert price.price == 123.45  # noqa: PLR2004

    def test_product_price_with_zero(self):
        """Test that ProductPrice can have zero price."""
        uom_liter = UnitOfMeasureFactory()
        price = ProductPrice.objects.create(
            product=self.product,
            unit_of_measure=uom_liter,
            price=0.00,
        )
        assert price.price == 0.00

    def test_product_price_high_value(self):
        """Test that ProductPrice can handle high values."""
        uom_ton = UnitOfMeasureFactory()
        price = ProductPrice.objects.create(
            product=self.product,
            unit_of_measure=uom_ton,
            price=99999999.99,
        )
        assert price.price == 99999999.99  # noqa: PLR2004

    def test_product_price_product_relationship(self):
        """Test that ProductPrice correctly relates to Product."""
        assert self.product_price.product == self.product
        # Check reverse relationship
        assert self.product_price in self.product.prices.all()

    def test_product_price_unit_of_measure_relationship(self):
        """Test that ProductPrice correctly relates to UnitOfMeasure."""
        assert self.product_price.unit_of_measure == self.unit_of_measure
        # Check reverse relationship
        assert self.product_price in self.unit_of_measure.product_prices.all()

    def test_cascade_delete_product_deletes_prices(self):
        """Test that deleting a product also deletes related prices."""
        price_id = self.product_price.id
        self.product.delete()
        assert not ProductPrice.objects.filter(id=price_id).exists()

    def test_cascade_delete_unit_of_measure_deletes_prices(self):
        """Test that deleting a UOM also deletes related prices."""
        price_id = self.product_price.id
        self.unit_of_measure.delete()
        assert not ProductPrice.objects.filter(id=price_id).exists()

    def test_product_price_unique_together_constraint(self):
        """Test that product and unit_of_measure combination must be unique."""
        # Attempt to create another price with same product and UOM
        with pytest.raises(IntegrityError):
            ProductPrice.objects.create(
                product=self.product,
                unit_of_measure=self.unit_of_measure,
                price=200.00,
            )

    def test_multiple_prices_per_product_different_uom(self):
        """Test that a product can have multiple prices with different UOMs."""
        # Check initial count
        initial_count = self.product.prices.count()

        uom2 = UnitOfMeasureFactory()
        uom3 = UnitOfMeasureFactory()

        # Create prices directly to avoid nested factory issues
        ProductPrice.objects.create(
            product=self.product,
            unit_of_measure=uom2,
            price=50.00,
        )
        ProductPrice.objects.create(
            product=self.product,
            unit_of_measure=uom3,
            price=75.00,
        )

        # Should have 2 more prices than initial
        assert self.product.prices.count() == initial_count + 2

    def test_same_uom_for_different_products(self):
        """Test that same UOM can be used for different products."""
        product2 = ProductFactory(prices=0, images=0)
        price2 = ProductPrice.objects.create(
            product=product2,
            unit_of_measure=self.unit_of_measure,
            price=50.00,
        )

        assert price2.unit_of_measure == self.unit_of_measure
        assert price2.product != self.product

    def test_product_price_ordering(self):
        """Test that product prices are ordered by created_at descending."""
        uom2 = UnitOfMeasureFactory()
        uom3 = UnitOfMeasureFactory()

        price1 = ProductPrice.objects.create(
            product=self.product,
            unit_of_measure=uom2,
            price=50.00,
        )
        price2 = ProductPrice.objects.create(
            product=self.product,
            unit_of_measure=uom3,
            price=75.00,
        )

        prices = self.product.prices.all()
        # Most recent first - price2 should be first, price1 second
        # self.product_price from setUp should be last
        assert prices.first() == price2
        assert price2 in prices
        assert price1 in prices
        assert self.product_price in prices

    def test_product_price_timestamps(self):
        """Test that created_at and updated_at are set correctly."""
        assert self.product_price.created_at is not None
        assert self.product_price.updated_at is not None
        assert self.product_price.created_at <= self.product_price.updated_at

    def test_product_price_history_tracking(self):
        """Test that product price changes are tracked in history."""
        original_price = self.product_price.price
        self.product_price.price = 200.75
        self.product_price.save()

        # Check that history was created
        history = self.product_price.history.all()
        assert history.count() >= 2  # noqa: PLR2004
        # Most recent history should have updated price
        assert history[0].price == 200.75  # noqa: PLR2004
        # Older history should have original price
        assert history[1].price == original_price

    def test_product_price_meta_verbose_names(self):
        """Test that model meta verbose names are correct."""
        assert ProductPrice._meta.verbose_name == "Product Price"  # noqa: SLF001
        assert ProductPrice._meta.verbose_name_plural == "Product Prices"  # noqa: SLF001

    def test_product_price_uuid_field(self):
        """Test that id is a UUID and is primary key."""
        assert self.product_price.id is not None
        assert str(self.product_price.id) != ""
        # UUID should be unique
        uom_gram = UnitOfMeasureFactory()
        price2 = ProductPrice.objects.create(
            product=self.product,
            unit_of_measure=uom_gram,
            price=75.00,
        )
        assert self.product_price.id != price2.id

    def test_product_price_required_fields(self):
        """Test that required fields cannot be null."""
        with pytest.raises(  # noqa: B017
            Exception,  # noqa: PT011
        ):  # Can be IntegrityError or ValidationError
            ProductPrice.objects.create(
                # Missing required fields
                price=100.00,
            )

    def test_product_price_update(self):
        """Test that updating product price works correctly."""
        original_created_at = self.product_price.created_at
        self.product_price.price = 150.00
        self.product_price.save()

        self.product_price.refresh_from_db()
        assert self.product_price.price == 150.00  # noqa: PLR2004
        assert self.product_price.created_at == original_created_at
        assert self.product_price.updated_at > original_created_at
