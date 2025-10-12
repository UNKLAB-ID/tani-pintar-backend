import uuid

import pytest
from django.db import IntegrityError
from django.test import TestCase

from ecommerce.models import UnitOfMeasure
from ecommerce.tests.factories import UnitOfMeasureFactory


class UnitOfMeasureModelTest(TestCase):
    def setUp(self):
        self.uom = UnitOfMeasureFactory(name="kilogram")

    def test_uom_creation(self):
        uom = UnitOfMeasure.objects.get(id=self.uom.id)
        assert uom.name == "kilogram"
        assert uom.created_at is not None
        assert uom.updated_at is not None

    def test_uom_str_representation(self):
        assert str(self.uom) == "kilogram"

    def test_uom_uuid_primary_key(self):
        assert isinstance(self.uom.id, uuid.UUID)

    def test_uom_unique_name_constraint(self):
        with pytest.raises(IntegrityError):
            UnitOfMeasure.objects.create(name="kilogram")

    def test_uom_optional_description(self):
        uom_without_desc = UnitOfMeasure.objects.create(
            name="meter",
            description="",
        )
        assert uom_without_desc.description == ""

        uom_with_desc = UnitOfMeasureFactory(
            name="liter",
            description="Unit of volume measurement",
        )
        assert uom_with_desc.description == "Unit of volume measurement"

    def test_uom_meta_verbose_names(self):
        assert UnitOfMeasure._meta.verbose_name == "Unit of Measure"  # noqa: SLF001
        assert UnitOfMeasure._meta.verbose_name_plural == "Units of Measure"  # noqa: SLF001

    def test_uom_ordering(self):
        uom_zebra = UnitOfMeasureFactory(name="zebra-unit")
        uom_alpha = UnitOfMeasureFactory(name="alpha-unit")
        uom_beta = UnitOfMeasureFactory(name="beta-unit")

        uoms = UnitOfMeasure.objects.all()

        # Should be ordered alphabetically by name
        assert uoms[0] == uom_alpha
        assert uoms[1] == uom_beta
        assert uoms[2] == self.uom  # kilogram
        assert uoms[3] == uom_zebra

    def test_uom_default_description(self):
        uom = UnitOfMeasure.objects.create(name="piece")
        assert uom.description == ""

    def test_uom_max_length_name(self):
        # Test that name field respects max_length of 50
        long_name = "a" * 50
        uom = UnitOfMeasure.objects.create(name=long_name)
        assert len(uom.name) == 50  # noqa: PLR2004

    def test_uom_historical_records(self):
        # Test that historical records are being tracked
        assert hasattr(self.uom, "history")
        assert self.uom.history.count() == 1

        # Update the UOM and check history
        self.uom.description = "Updated description"
        self.uom.save()

        assert self.uom.history.count() == 2  # noqa: PLR2004

    def test_uom_timestamps_update(self):
        original_updated_at = self.uom.updated_at

        # Update the UOM
        self.uom.description = "New description"
        self.uom.save()

        # Refresh from database
        self.uom.refresh_from_db()

        # Check that updated_at changed
        assert self.uom.updated_at > original_updated_at
        # created_at should remain the same
        assert self.uom.created_at is not None

    def test_uom_blank_description_allowed(self):
        uom = UnitOfMeasureFactory(name="gram", description="")
        assert uom.description == ""

        uom_reloaded = UnitOfMeasure.objects.get(id=uom.id)
        assert uom_reloaded.description == ""
