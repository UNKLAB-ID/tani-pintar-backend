from django.conf import settings
from django.db import migrations


def _update_or_create_site_with_sequence(site_model, connection, domain, name):
    """Update or create the site with default ID and keep the DB sequence in sync."""
    site, created = site_model.objects.update_or_create(
        id=settings.SITE_ID,
        defaults={
            "domain": domain,
            "name": name,
        },
    )
    if created:
        # For TiDB, we need to use a different approach to update auto-increment value
        max_id = site_model.objects.order_by("-id").first().id
        with connection.cursor() as cursor:
            # TiDB uses AUTO_INCREMENT instead of sequences
            cursor.execute(
                f"ALTER TABLE django_site AUTO_INCREMENT = %s",
                [max_id + 1],
            )


def update_site_forward(apps, schema_editor):
    """Set site domain and name."""
    Site = apps.get_model("sites", "Site")
    _update_or_create_site_with_sequence(
        Site,
        schema_editor.connection,
        "example.com",
        "Tani Pintar",
    )


def update_site_backward(apps, schema_editor):
    """Revert site domain and name to default."""
    Site = apps.get_model("sites", "Site")
    _update_or_create_site_with_sequence(
        Site,
        schema_editor.connection,
        "example.com",
        "example.com",
    )


class Migration(migrations.Migration):

    dependencies = [("sites", "0002_alter_domain_unique")]

    operations = [migrations.RunPython(update_site_forward, update_site_backward)]