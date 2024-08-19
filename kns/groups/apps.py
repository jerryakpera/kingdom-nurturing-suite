"""
Django AppConfig for the `groups` app.
"""

from django.apps import AppConfig


class GroupsConfig(AppConfig):
    """
    Configuration for the `groups` app in the Django project.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "kns.groups"
