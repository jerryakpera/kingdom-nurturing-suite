"""
Django AppConfig for the `events` app.
"""

from django.apps import AppConfig


class EventsConfig(AppConfig):
    """
    Configuration for the `events` app in the Django project.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "kns.events"
