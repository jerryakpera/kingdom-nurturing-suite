"""
App configuration for the 'faith_milestones' application.
"""

from django.apps import AppConfig


class MilestonesConfig(AppConfig):
    """
    Configuration class for the 'faith_milestones' application.

    This class sets up the default configuration for the 'faith_milestones'
    app within the Kingdom Nurturing Suite (KNS) project.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "kns.faith_milestones"
