"""
Django AppConfig for the profiles app.
"""

from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """
    Configuration for the `core` app in the Django project.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "kns.profiles"
