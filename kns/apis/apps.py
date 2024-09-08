"""
Django AppConfig for the `apis` app.
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Configuration class for the `apis` app. This class sets the app name and
    the default type of auto-generated primary key fields for models.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "kns.apis"
