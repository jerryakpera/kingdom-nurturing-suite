"""
User model definition for the application.
"""

from django.db import models
from django_use_email_as_username.models import BaseUser, BaseUserManager


class User(BaseUser):
    """
    Custom user model extending BaseUser.

    Attributes:
        objects (BaseUserManager): The manager for the `User` model,
        which provides methods for creating and managing user instances.
    """

    objects = BaseUserManager()

    # User settings
    verified = models.BooleanField(default=False)
    is_visitor = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=False)
