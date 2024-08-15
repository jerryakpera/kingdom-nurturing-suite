"""
This module contains abstract base models that are useful for providing common
fields and functionality across different Django models.
"""

from django.db import models


class TimestampedModel(models.Model):
    """
    An abstract base model that provides `created_at` and `updated_at` fields
    to track when the model instance was created and last updated.

    Fields:
        created_at (DateTimeField): Automatically set to the date
        and time when the instance is first created.
        updated_at (DateTimeField): Automatically updated to the date
        and time when the instance is last updated.

    Usage:
        This model is useful for any other models that need to keep track of
        creation and modification times.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
    )

    class Meta:
        abstract = True
