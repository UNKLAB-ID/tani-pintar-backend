from accounts.tests.factories import ProfileFactory

def run():
    ProfileFactory.create_batch(10)