"""
Django app configuration for the skills app.
"""

from django.apps import AppConfig


class SkillsConfig(AppConfig):
    """
    Configuration class for the skills app.

    This class defines the configuration for the 'skills' app,
    including its name and default auto field type.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "kns.skills"
