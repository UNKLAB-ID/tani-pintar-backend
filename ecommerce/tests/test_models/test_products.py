import uuid

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from core.users.tests.factories import UserFactory
from ecommerce.models import Product
from ecommerce.models import ProductImage
from ecommerce.tests.factories import ProductCategoryFactory
from ecommerce.tests.factories import ProductFactory
from ecommerce.tests.factories import ProductImageFactory


class ProductModelTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.category = ProductCategoryFactory(name="Electronics")
        self.product = ProductFactory(
            name="Test Product",
            user=self.user,
            category=self.category,
        )

    def test_product_creation(self):
        product = Product.objects.get(uuid=self.product.uuid)
        assert product.name == "Test Product"
        assert product.user == self.user
        assert product.category == self.category
        assert product.status == Product.STATUS_ACTIVE
        assert product.approval_status == Product.APPROVAL_APPROVED
        assert product.available_stock >= 0
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_product_str_representation(self):
        assert str(self.product) == "Test Product"

    def test_product_uuid_primary_key(self):
        assert isinstance(self.product.uuid, uuid.UUID)

    def test_product_auto_slug_generation(self):
        product = ProductFactory(name="Gaming Laptop Pro")
        assert product.slug == slugify("Gaming Laptop Pro")

    def test_product_slug_uniqueness_with_counter(self):
        product1 = ProductFactory(name="Test Item")
        product2 = Product(
            name="Test Item",
            user=self.user,
            category=self.category,
            description="Test description",
            available_stock=10,
        )
        product2.save()

        assert product1.slug == "test-item"
        assert product2.slug == "test-item-1"

    def test_product_unique_slug_constraint(self):
        ProductFactory(name="Test Product", slug="test-slug")
        with pytest.raises(IntegrityError):
            Product.objects.create(
                name="Another Product",
                user=self.user,
                category=self.category,
                slug="test-slug",
                description="Test description",
                available_stock=10,
            )

    def test_product_slug_generated_when_empty(self):
        product = Product(
            name="Sports Equipment",
            user=self.user,
            category=self.category,
            description="Test description",
            available_stock=10,
        )
        product.save()
        assert product.slug == "sports-equipment"

    def test_product_slug_not_overwritten_when_exists(self):
        product = Product(
            name="Test Product",
            user=self.user,
            category=self.category,
            slug="custom-slug",
            description="Test description",
            available_stock=10,
        )
        product.save()
        assert product.slug == "custom-slug"

    def test_product_status_choices(self):
        assert Product.STATUS_DRAFT == "draft"
        assert Product.STATUS_ACTIVE == "active"
        assert Product.STATUS_INACTIVE == "inactive"

        product_draft = ProductFactory(status=Product.STATUS_DRAFT)
        product_active = ProductFactory(status=Product.STATUS_ACTIVE)
        product_inactive = ProductFactory(status=Product.STATUS_INACTIVE)

        assert product_draft.status == "draft"
        assert product_active.status == "active"
        assert product_inactive.status == "inactive"

    def test_product_approval_choices(self):
        assert Product.APPROVAL_PENDING == "pending"
        assert Product.APPROVAL_APPROVED == "approved"
        assert Product.APPROVAL_REJECTED == "rejected"

        product_pending = ProductFactory(approval_status=Product.APPROVAL_PENDING)
        product_approved = ProductFactory(approval_status=Product.APPROVAL_APPROVED)
        product_rejected = ProductFactory(approval_status=Product.APPROVAL_REJECTED)

        assert product_pending.approval_status == "pending"
        assert product_approved.approval_status == "approved"
        assert product_rejected.approval_status == "rejected"

    def test_product_default_values(self):
        product = Product.objects.create(
            name="Test Default",
            user=self.user,
            category=self.category,
            description="Test description",
        )
        assert product.available_stock == 0
        assert product.status == Product.STATUS_DRAFT
        assert product.approval_status == Product.APPROVAL_PENDING

    def test_product_cascade_delete_on_user_deletion(self):
        product_uuid = self.product.uuid
        self.user.delete()

        with pytest.raises(Product.DoesNotExist):
            Product.objects.get(uuid=product_uuid)

    def test_product_cascade_delete_on_category_deletion(self):
        product_uuid = self.product.uuid
        self.category.delete()

        with pytest.raises(Product.DoesNotExist):
            Product.objects.get(uuid=product_uuid)

    def test_product_related_name_access_from_user(self):
        product2 = ProductFactory(user=self.user)
        products = self.user.products.all()

        assert self.product in products
        assert product2 in products
        assert products.count() == 2  # noqa: PLR2004

    def test_product_related_name_access_from_category(self):
        product2 = ProductFactory(category=self.category)
        products = self.category.products.all()

        assert self.product in products
        assert product2 in products
        assert products.count() == 2  # noqa: PLR2004

    def test_product_meta_attributes(self):
        assert Product._meta.verbose_name == "Product"  # noqa: SLF001
        assert Product._meta.verbose_name_plural == "Products"  # noqa: SLF001
        assert Product._meta.ordering == ["-created_at"]  # noqa: SLF001

    def test_product_available_stock_positive_integer(self):
        product = ProductFactory(available_stock=100)
        assert product.available_stock == 100  # noqa: PLR2004

        product.available_stock = 0
        product.save()
        assert product.available_stock == 0

    def test_product_required_fields(self):
        product = Product(name="Test Product")
        with pytest.raises((IntegrityError, ValueError)):
            product.save()

    def test_product_image_field(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg",
        )
        product = ProductFactory(image=image)
        assert product.image is not None
        assert "ecommerce/products/images/" in product.image.name

    def test_product_ordering(self):
        older_product = ProductFactory()
        newer_product = ProductFactory()

        products = Product.objects.all()
        assert products[0] == newer_product
        assert products[1] == older_product

    def test_product_multiple_slug_collision_handling(self):
        ProductFactory(name="Duplicate Name")
        ProductFactory(name="Duplicate Name")
        ProductFactory(name="Duplicate Name")

        products = Product.objects.filter(name="Duplicate Name").order_by("slug")
        assert products[0].slug == "duplicate-name"
        assert products[1].slug == "duplicate-name-1"
        assert products[2].slug == "duplicate-name-2"


class ProductImageModelTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.category = ProductCategoryFactory()
        self.product = ProductFactory(
            user=self.user,
            category=self.category,
        )
        self.product_image = ProductImageFactory(
            product=self.product,
            caption="Test Image Caption",
        )

    def test_product_image_creation(self):
        product_image = ProductImage.objects.get(id=self.product_image.id)
        assert product_image.product == self.product
        assert product_image.caption == "Test Image Caption"
        assert product_image.created_at is not None

    def test_product_image_str_representation(self):
        expected_str = f"{self.product.name} - Image {self.product_image.pk}"
        assert str(self.product_image) == expected_str

    def test_product_image_cascade_delete_on_product_deletion(self):
        image_id = self.product_image.id
        self.product.delete()

        with pytest.raises(ProductImage.DoesNotExist):
            ProductImage.objects.get(id=image_id)

    def test_product_image_related_name_access(self):
        image2 = ProductImageFactory(product=self.product)
        product_images = self.product.images.all()

        assert self.product_image in product_images
        assert image2 in product_images
        assert product_images.count() >= 2  # noqa: PLR2004

    def test_product_image_meta_attributes(self):
        assert ProductImage._meta.verbose_name == "Product Image"  # noqa: SLF001
        assert ProductImage._meta.verbose_name_plural == "Product Images"  # noqa: SLF001
        assert ProductImage._meta.ordering == ["created_at"]  # noqa: SLF001

    def test_product_image_default_values(self):
        image = ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile(
                "test.jpg",
                b"file_content",
                content_type="image/jpeg",
            ),
        )
        assert image.caption == ""

    def test_product_image_optional_caption(self):
        image_no_caption = ProductImageFactory(
            product=self.product,
            caption="",
        )
        assert image_no_caption.caption == ""

        image_with_caption = ProductImageFactory(
            product=self.product,
            caption="Beautiful product image",
        )
        assert image_with_caption.caption == "Beautiful product image"

    def test_product_image_file_upload_path(self):
        image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg",
        )
        product_image = ProductImageFactory(
            product=self.product,
            image=image,
        )
        assert "ecommerce/products/images/" in product_image.image.name

    def test_product_image_ordering(self):
        older_image = ProductImageFactory(product=self.product)
        newer_image = ProductImageFactory(product=self.product)

        images = self.product.images.all()
        image_list = list(images)
        assert older_image in image_list
        assert newer_image in image_list
        assert len(image_list) >= 2  # noqa: PLR2004

    def test_product_image_required_fields(self):
        product_image = ProductImage()
        with pytest.raises((IntegrityError, ValueError)):
            product_image.save()

    def test_product_image_caption_max_length(self):
        valid_caption = "a" * 200
        image = ProductImageFactory(
            product=self.product,
            caption=valid_caption,
        )
        assert len(image.caption) == 200  # noqa: PLR2004

    def test_multiple_product_images_relationship(self):
        product1 = ProductFactory()
        product2 = ProductFactory()

        image1_1 = ProductImageFactory(product=product1)
        image1_2 = ProductImageFactory(product=product1)
        image2_1 = ProductImageFactory(product=product2)

        product1_images = product1.images.all()
        product2_images = product2.images.all()

        assert image1_1 in product1_images
        assert image1_2 in product1_images
        assert image2_1 in product2_images
        assert image2_1 not in product1_images
