"""
Django AppConfig for the core app.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration for the `core` app in the Django project.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "kns.core"
