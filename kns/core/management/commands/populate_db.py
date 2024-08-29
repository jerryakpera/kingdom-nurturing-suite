"""
This module defines a custom Django management command to populate the
database with initial data.
"""

from django.core.management.base import BaseCommand

from kns.skills.skills_data import skills as skills_data
from kns.skills.utils import populate_skills


class Command(BaseCommand):
    """
    Custom Django management command to populate the database with
    initial skill data.
    """

    help = "Populates the database with initial data."

    def handle(self, *args, **options):
        """
        Handle the execution of the populate_skills command.

        Parameters
        ----------
        *args : tuple
            Additional positional arguments.
        **options : dict
            Additional keyword arguments.
        """
        populate_skills(skills_data=skills_data)

        print("Database successfully populated.")
