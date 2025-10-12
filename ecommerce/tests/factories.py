import factory
from factory import Faker
from factory.django import DjangoModelFactory

from ecommerce.models import ProductCategory
from ecommerce.models import ProductSubCategory
from ecommerce.models import UnitOfMeasure


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
