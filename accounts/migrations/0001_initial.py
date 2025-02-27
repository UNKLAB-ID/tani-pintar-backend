# Generated by Django 4.2.17 on 2025-01-02 08:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('full_name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=20, unique=True)),
                ('profile_type', models.CharField(choices=[('Farmer', 'Farmer'), ('Distributor', 'Distributor'), ('Consumer', 'Consumer'), ('Supplier', 'Supplier'), ('Agent', 'Agent'), ('Vendor', 'Vendor')], default='Farmer', max_length=25)),
                ('id_card_file', models.FileField(upload_to='id-card-images/')),
                ('id_card_validation_status', models.CharField(choices=[('Pending', 'Pending'), ('Verified', 'Verified'), ('Rejected', 'Rejected'), ('Resubmission', 'Resubmission'), ('Expired', 'Expired')], default='Pending', max_length=25)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
