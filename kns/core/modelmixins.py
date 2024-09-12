"""
This module contains abstract base models that are useful for providing common
fields and functionality across different Django models.
"""

from django.db import models
from django_countries.fields import CountryField

from . import constants


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


class ModelWithStatus(models.Model):
    """
    An abstract Django model that provides a status field for models
    that require a state or status indicator.

    This abstract model includes the following field:
    - `status`: A CharField that stores the status of the model.
      It uses `STATUS_CHOICES` from the constants module to define
      the available options. The default value is "published" and the
      maximum length is 10 characters.

    Subclasses of this model will inherit this field and can use it to
    track the status of an object. Like all abstract models, this class
    cannot be used directly to create database tables.
    """

    status = models.CharField(
        choices=constants.STATUS_CHOICES,
        default="published",
        max_length=10,
    )

    class Meta:
        abstract = True
