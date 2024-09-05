"""
This module defines a custom Django management command to populate the
database with initial data.
"""

from django.core.management.base import BaseCommand

from kns.faith_milestones.db_data import milestones as milestones_data
from kns.faith_milestones.utils import populate_faith_milestones
from kns.profiles.db_data import encryption_reasons
from kns.profiles.utils import populate_encryption_reasons
from kns.skills.skills_data import skills as skills_data
from kns.skills.utils import populate_skills
from kns.vocations.utils import populate_vocations
from kns.vocations.vocations_data import vocations as vocations_data


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
        populate_faith_milestones(
            faith_milestones_data=milestones_data,
        )
        populate_encryption_reasons(
            encryption_reasons_data=encryption_reasons,
        )
        populate_vocations(
            vocations_data=vocations_data,
        )

        print("Database successfully populated.")
