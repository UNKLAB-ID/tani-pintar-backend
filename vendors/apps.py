from django.apps import AppConfig


class VendorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "vendors"

    def ready(self):
        """Import signal handlers when Django starts."""
        import vendors.signals  # noqa: F401
