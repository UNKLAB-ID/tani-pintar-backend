import factory

from accounts.models import Profile
from accounts.tests.factories import ProfileFactory
from social_media.models import Post
from social_media.models import PostComment
from social_media.models import PostImage
from social_media.models import PostLike


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    user = factory.LazyAttribute(
        lambda _: ProfileFactory(profile_type=Profile.FARMER).user,
    )
    content = factory.Faker("paragraph", nb_sentences=10)

    @factory.post_generation
    def images(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for _ in range(extracted):
                PostImageFactory(post=self, **kwargs)
        else:
            for _ in range(3):
                PostImageFactory(post=self)


class PostImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostImage

    post = factory.SubFactory(PostFactory)
    image = factory.django.ImageField(color="blue")  # Simulasi file gambar


class PostCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostComment

    post = factory.SubFactory(PostFactory)
    user = factory.LazyAttribute(
        lambda _: ProfileFactory(profile_type=Profile.FARMER).user,
    )
    content = factory.Faker("paragraph", nb_sentences=3)
    parent = None


class PostLikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostLike

    post = factory.SubFactory(PostFactory)
    user = factory.LazyAttribute(
        lambda _: ProfileFactory(profile_type=Profile.FARMER).user,
    )
