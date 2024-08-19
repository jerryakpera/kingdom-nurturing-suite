"""
This module contains abstract base models that are useful for providing common
fields and functionality across different Django models.
"""

from django.db import models
from django_countries.fields import CountryField


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


class ModelWithLocation(models.Model):
    """
    An abstract Django model that provides fields for storing
    location information.

    This abstract model includes the following fields:
    - `location_country`: A CountryField to store the country of the location.
      This field can be null or blank.
    - `location_city`: A CharField to store the city of the location.
      This field can be null or blank.

    Subclasses of this model will inherit these fields and can use them to
    store location-related information. Since this model is abstract, it
    cannot be used directly to create database tables.
    """

    location_country = CountryField(
        null=True,
        blank=True,
    )
    location_city = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
