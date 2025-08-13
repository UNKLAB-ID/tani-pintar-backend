import factory
from factory import Faker
from factory.django import DjangoModelFactory

from core.users.tests.factories import UserFactory
from ecommerce.models import Product
from ecommerce.models import ProductCategory
from ecommerce.models import ProductImage
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


class ProductFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(ProductCategoryFactory)
    image = factory.django.ImageField(color="green")
    name = Faker("word")
    description = Faker("text", max_nb_chars=500)
    available_stock = Faker("random_int", min=0, max=1000)
    status = Product.STATUS_ACTIVE
    approval_status = Product.APPROVAL_APPROVED

    class Meta:
        model = Product

    @factory.post_generation
    def images(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for _ in range(extracted):
                ProductImageFactory(product=self, **kwargs)
        else:
            for _ in range(2):
                ProductImageFactory(product=self)


class ProductImageFactory(DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField(color="blue")
    caption = Faker("sentence", nb_words=4)

    class Meta:
        model = ProductImage
