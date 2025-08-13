import uuid

import pytest
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from ecommerce.models import ProductCategory
from ecommerce.models import ProductSubCategory
from ecommerce.tests.factories import ProductCategoryFactory
from ecommerce.tests.factories import ProductSubCategoryFactory


class ProductCategoryModelTest(TestCase):
    def setUp(self):
        self.category = ProductCategoryFactory(name="Electronics")

    def test_category_creation(self):
        category = ProductCategory.objects.get(id=self.category.id)
        assert category.name == "Electronics"
        assert category.is_active is True
        assert category.is_featured is False
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_category_str_representation(self):
        assert str(self.category) == "Electronics"

    def test_category_uuid_primary_key(self):
        assert isinstance(self.category.id, uuid.UUID)

    def test_category_auto_slug_generation(self):
        category = ProductCategoryFactory(name="Home & Garden")
        assert category.slug == slugify("Home & Garden")

    def test_category_unique_name_constraint(self):
        with pytest.raises(IntegrityError):
            ProductCategory.objects.create(name="Electronics")

    def test_category_unique_slug_constraint(self):
        ProductCategoryFactory(name="Test Category", slug="test-slug")
        with pytest.raises(IntegrityError):
            ProductCategory.objects.create(
                name="Another Category",
                slug="test-slug",
            )

    def test_category_slug_generated_when_empty(self):
        category = ProductCategory(name="Sports Equipment")
        category.save()
        assert category.slug == "sports-equipment"

    def test_category_slug_not_overwritten_when_exists(self):
        category = ProductCategory(name="Test Category", slug="custom-slug")
        category.save()
        assert category.slug == "custom-slug"

    def test_category_meta_verbose_names(self):
        assert ProductCategory._meta.verbose_name == "Categorys"  # noqa: SLF001
        assert ProductCategory._meta.verbose_name_plural == "Categories"  # noqa: SLF001

    def test_category_default_values(self):
        category = ProductCategory.objects.create(name="Test Default")
        assert category.is_active is True
        assert category.is_featured is False
        assert category.description is None

    def test_category_optional_description(self):
        category = ProductCategoryFactory(description=None)
        assert category.description is None

        category_with_desc = ProductCategoryFactory(description="Test description")
        assert category_with_desc.description == "Test description"


class ProductSubCategoryModelTest(TestCase):
    def setUp(self):
        self.category = ProductCategoryFactory(name="Electronics")
        self.subcategory = ProductSubCategoryFactory(
            name="Laptops",
            category=self.category,
        )

    def test_subcategory_creation(self):
        subcategory = ProductSubCategory.objects.get(id=self.subcategory.id)
        assert subcategory.name == "Laptops"
        assert subcategory.category == self.category
        assert subcategory.is_active is True
        assert subcategory.is_featured is False
        assert subcategory.created_at is not None
        assert subcategory.updated_at is not None

    def test_subcategory_str_representation(self):
        expected_str = f"{self.category.name} > {self.subcategory.name}"
        assert str(self.subcategory) == expected_str

    def test_subcategory_uuid_primary_key(self):
        assert isinstance(self.subcategory.id, uuid.UUID)

    def test_subcategory_auto_slug_generation(self):
        subcategory = ProductSubCategoryFactory(
            name="Gaming Laptops",
            category=self.category,
        )
        expected_slug = slugify(f"{self.category.name}-Gaming Laptops")
        assert subcategory.slug == expected_slug

    def test_subcategory_slug_uniqueness_with_counter(self):
        subcategory1 = ProductSubCategoryFactory(
            name="Test Item",
            category=self.category,
        )
        subcategory2 = ProductSubCategory(
            name="Test Item",
            category=self.category,
        )
        subcategory2.save()

        assert subcategory1.slug == "electronics-test-item"
        assert subcategory2.slug == "electronics-test-item-1"

    def test_subcategory_cascade_delete_on_category_deletion(self):
        subcategory_id = self.subcategory.id
        self.category.delete()

        with pytest.raises(ProductSubCategory.DoesNotExist):
            ProductSubCategory.objects.get(id=subcategory_id)

    def test_subcategory_related_name_access(self):
        subcategory2 = ProductSubCategoryFactory(
            name="Smartphones",
            category=self.category,
        )

        subcategories = self.category.subcategories.all()
        assert self.subcategory in subcategories
        assert subcategory2 in subcategories
        assert subcategories.count() == 2  # noqa: PLR2004

    def test_subcategory_meta_attributes(self):
        assert ProductSubCategory._meta.verbose_name == "Product SubCategory"  # noqa: SLF001
        assert ProductSubCategory._meta.verbose_name_plural == "Product SubCategories"  # noqa: SLF001
        assert ProductSubCategory._meta.ordering == ["category", "name"]  # noqa: SLF001

    def test_subcategory_default_values(self):
        subcategory = ProductSubCategory.objects.create(
            name="Test Default",
            category=self.category,
        )
        assert subcategory.is_active is True
        assert subcategory.is_featured is False
        assert subcategory.description is None

    def test_subcategory_optional_description(self):
        subcategory = ProductSubCategoryFactory(
            category=self.category,
            description=None,
        )
        assert subcategory.description is None

        subcategory_with_desc = ProductSubCategoryFactory(
            category=self.category,
            description="Test subcategory description",
        )
        assert subcategory_with_desc.description == "Test subcategory description"

    def test_subcategory_slug_generation_with_different_categories(self):
        category2 = ProductCategoryFactory(name="Fashion")

        subcategory1 = ProductSubCategoryFactory(
            name="Accessories",
            category=self.category,
        )
        subcategory2 = ProductSubCategoryFactory(
            name="Accessories",
            category=category2,
        )

        assert subcategory1.slug == "electronics-accessories"
        assert subcategory2.slug == "fashion-accessories"

    def test_subcategory_ordering(self):
        # Create additional subcategories in the same category to test name ordering
        subcategory_alpha = ProductSubCategoryFactory(
            name="Alpha",
            category=self.category,
        )
        subcategory_zebra = ProductSubCategoryFactory(
            name="Zebra",
            category=self.category,
        )

        subcategories = self.category.subcategories.all()

        # Should be ordered by subcategory name within the same category
        # Since ordering is ["category", "name"], subcategories within the same category
        # should be ordered alphabetically by name
        assert subcategories[0] == subcategory_alpha  # Alpha comes first
        assert subcategories[1] == self.subcategory  # Laptops comes second
        assert subcategories[2] == subcategory_zebra  # Zebra comes last
