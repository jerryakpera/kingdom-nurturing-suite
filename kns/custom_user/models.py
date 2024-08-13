"""
User model definition for the application.
"""

from django_use_email_as_username.models import BaseUser, BaseUserManager


class User(BaseUser):
    """
    Custom user model extending BaseUser.

    Attributes:
        objects (BaseUserManager): The manager for the `User` model,
        which provides methods for creating and managing user instances.
    """

    objects = BaseUserManager()
