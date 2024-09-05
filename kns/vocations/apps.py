"""
Django AppConfig for the `vocations` app.
"""

from django.apps import AppConfig


class VocationsConfig(AppConfig):
    """
    Configuration class for the `vocations` Django application.

    Attributes
    ----------
    default_auto_field : str
        Specifies the default type of primary key fields to use for models in this application.
    name : str
        The full Python path to the application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "kns.vocations"
