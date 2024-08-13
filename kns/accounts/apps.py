"""
Django AppConfig for the accounts app.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration for the `accounts` app in the Django project.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "kns.accounts"
