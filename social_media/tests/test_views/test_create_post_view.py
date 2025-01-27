import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status

from accounts.models import Profile
from accounts.tests.factories import ProfileFactory


class CreatePostTest(TestCase):
    def setUp(self):
        self.url = reverse("social-media:post")
        self.profile = ProfileFactory(profile_type=Profile.FARMER)
        self.user = self.profile.user
        self.client.force_login(self.user)

    def create_dummy_image(self, image_name):
        img = Image.new("RGB", (100, 100), color="red")
        byte_io = io.BytesIO()
        img.save(byte_io, format="JPEG")
        byte_io.seek(0)
        return SimpleUploadedFile(image_name, byte_io.read(), content_type="image/jpeg")

    def test_create_post_success(self):
        image_1 = self.create_dummy_image("alpha.jpg")
        image_2 = self.create_dummy_image("beta.jpg")
        image_3 = self.create_dummy_image("gamma.jpg")

        data = {
            "content": "This is the content of the post.",
            "images": [image_1, image_2, image_3],
        }

        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json().get("content") is not None
        assert len(response.json().get("images")) == 3, "Images count must be 3"  # noqa: PLR2004
