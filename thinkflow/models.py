import json
import uuid
from pathlib import Path

from django.db import models
from django.utils import timezone

from core.users.models import User
from thinkflow.utils.plant_disease_checker import PlantDiseaseChecker


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
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    uuid = models.UUIDField(
        primary_key=False,
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to=plant_disease_image_path)

    # Disease analysis fields
    disease_name = models.CharField(max_length=255, blank=True, default="")
    confidence = models.FloatField(null=True, blank=True)
    symptoms = models.JSONField(null=True, blank=True)
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default="low",
    )
    treatment_recommendations = models.JSONField(null=True, blank=True)
    preventive_measures = models.JSONField(null=True, blank=True)
    mini_article = models.TextField(blank=True, default="")

    # Metadata fields
    created_at = models.DateTimeField(auto_now_add=True)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Plant Disease Analysis"
        verbose_name_plural = "Plant Disease Analyses"

    def __str__(self):
        return f"{self.uuid} - {self.disease_name}"

    def analyze(self):
        plant_disease_checker = PlantDiseaseChecker()
        result = plant_disease_checker.analyze_by_image_field(self.image)

        output_text = json.loads(result.output_text)

        self.disease_name = output_text.get("disease_name", "")
        self.confidence = output_text.get("confidence", 0)
        self.symptoms = output_text.get("symptoms", [])
        self.severity = output_text.get("severity", "low")
        self.treatment_recommendations = output_text.get(
            "treatment_recommendations",
            [],
        )
        self.preventive_measures = output_text.get("preventive_measures", [])
        self.mini_article = output_text.get("mini_article", "")
        self.input_tokens = result.usage.input_tokens
        self.output_tokens = result.usage.output_tokens
        self.total_tokens = result.usage.total_tokens
        self.save()
