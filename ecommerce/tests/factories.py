import factory
from factory import Faker
from factory.django import DjangoModelFactory

from ecommerce.models import ProductCategory
from ecommerce.models import ProductSubCategory


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
