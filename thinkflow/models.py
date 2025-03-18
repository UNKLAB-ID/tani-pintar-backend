import uuid
from pathlib import Path

from django.db import models
from django.utils import timezone

from core.users.models import User


def plant_disease_image_path(instance, filename):
    # Get the file extension
    ext = filename.split(".")[-1]
    # Format path as: plant_disease_images/YYYY/MM/DD/filename
    today = timezone.localdate()
    path = f"plant_disease_images/{today.year}/{today.month:02d}/{today.day:02d}"
    # Create a filename with the uuid to ensure uniqueness
    filename = f"{instance.uuid}.{ext}"
    return str(Path(path) / filename)


class PlantDisease(models.Model):
    uuid = models.UUIDField(
        primary_key=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    details = models.TextField()
    image = models.ImageField(upload_to=plant_disease_image_path)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uuid
