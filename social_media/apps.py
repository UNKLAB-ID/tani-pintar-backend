from django.apps import AppConfig


class SocialMediaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "social_media"

    def ready(self):
        """Import signal handlers when Django starts."""
        import social_media.signals  # noqa: F401
