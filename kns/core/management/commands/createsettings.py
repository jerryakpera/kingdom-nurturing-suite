"""
Django management command to ensure the initialization of the Setting model instance.

This command checks if an instance of the Setting model exists. If not, it creates
a default instance to ensure the necessary settings are available for the application.

Usage:
    python manage.py <command_name>
"""

from django.core.management.base import BaseCommand

from kns.core.models import Setting


class Command(BaseCommand):
    """
    Django management command that ensures the initialization of the
    Setting model instance. If an instance of Setting does not exist,
    this command will create one.
    """

    help = "Initializes settings."

    def handle(self, *args, **options):
        """
        The entry point for the command execution. This method calls
        the Setting model's get_or_create_setting method to ensure that
        a Setting instance exists. If none exists, it creates one.

        Parameters
        ----------
        *args
            Positional arguments passed to the command (not used in this
            method).
        **options
            Keyword arguments passed to the command (not used in this
            method).
        """
        Setting.get_or_create_setting()
        self.stdout.write(
            self.style.SUCCESS("Settings have been initialized."),
        )
