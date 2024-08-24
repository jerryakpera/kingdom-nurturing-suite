import pytest
from django.db import models

from ..modelmixins import TimestampedModel


class ExampleModel(TimestampedModel, models.Model):
    pass


class TestTimestampedModelMixin:
    def test_timestamps_on_creation(self):
        """
        Test that `created_at` and `updated_at` are set correctly
        upon creation of a model instance.
        """
        example_instance = ExampleModel.objects.create()

        # Check that `created_at` is set and `updated_at` is set
        assert example_instance.created_at is not None
        assert example_instance.updated_at is not None

        # Normalize `created_at` and `updated_at` to date, hour, and minute only
        created_at_normalized = example_instance.created_at.replace(
            second=0, microsecond=0
        )
        updated_at_normalized = example_instance.updated_at.replace(
            second=0, microsecond=0
        )

        # Assert that the normalized timestamps are equal
        assert created_at_normalized == updated_at_normalized, (
            f"Expected `created_at` and `updated_at` to be equal when normalized. "
            f"Got created_at={created_at_normalized} and updated_at={updated_at_normalized}"
        )
