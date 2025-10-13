import factory
from factory import Faker
from factory.django import DjangoModelFactory
from factory.django import ImageField

from ecommerce.models import Product
from ecommerce.models import ProductCategory
from ecommerce.models import ProductSubCategory
from ecommerce.models import UnitOfMeasure
from vendors.models import Vendor
from vendors.tests.factories import VendorFactory


class ProductCategoryFactory(DjangoModelFactory):
    name = Faker("word")
    description = Faker("text", max_nb_chars=200)
    is_active = True
    is_featured = False

    class Meta:
        model = ProductCategory
        django_get_or_create = ["name"]


class ProductSubCategoryFactory(DjangoModelFactory):
    name = Faker("word")
    description = Faker("text", max_nb_chars=200)
    category = factory.SubFactory(ProductCategoryFactory)
    is_active = True
    is_featured = False

    class Meta:
        model = ProductSubCategory


class UnitOfMeasureFactory(DjangoModelFactory):
    name = factory.Iterator(
        [
            "kilogram",
            "gram",
            "liter",
            "milliliter",
            "piece",
            "dozen",
            "box",
            "bag",
            "bottle",
            "can",
            "meter",
            "centimeter",
            "ton",
            "quintal",
            "pack",
        ],
    )
    description = Faker("text", max_nb_chars=200)

    class Meta:
        model = UnitOfMeasure
        django_get_or_create = ["name"]


class ProductFactory(DjangoModelFactory):
    vendor = factory.SubFactory(VendorFactory, review_status=Vendor.STATUS_APPROVED)
    user = factory.LazyAttribute(lambda o: o.vendor.user)
    category = factory.SubFactory(ProductCategoryFactory)
    image = ImageField(filename="product_image.jpg")
    name = Faker("word")
    description = Faker("text", max_nb_chars=500)
    available_stock = Faker("random_int", min=0, max=1000)
    status = Product.STATUS_ACTIVE
    approval_status = Product.APPROVAL_APPROVED

    class Meta:
        model = Product
        exclude = ["vendor"]
