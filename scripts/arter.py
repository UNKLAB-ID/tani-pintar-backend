from social_media.tests.factories import PostFactory


def run():
    PostFactory.create_batch(50)
