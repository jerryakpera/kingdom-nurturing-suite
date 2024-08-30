"""
This module defines a custom Django management command to populate the
database with initial data.
"""

from django.core.management.base import BaseCommand

from kns.profiles.db_data import encryption_reasons
from kns.profiles.utils import populate_encryption_reasons
from kns.skills.skills_data import skills as skills_data
from kns.skills.utils import populate_skills


class Command(BaseCommand):
    """
    Custom Django management command to populate the database with
    initial data.
    """

    help = "Populates the database with initial data."

    def handle(self, *args, **options):
        """
        Handle the execution of the populate_db command.

        Parameters
        ----------
        *args : tuple
            Additional positional arguments.
        **options : dict
            Additional keyword arguments.
        """
        populate_skills(skills_data=skills_data)
        populate_encryption_reasons(encryption_reasons_data=encryption_reasons)

        print("Database successfully populated.")
