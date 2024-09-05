"""
Utility functions for the `vocations` app.
"""

from kns.profiles.models import Profile

from .models import Vocation


def populate_vocations(vocations_data):
    """
    Populate the database with vocation data.

    This function iterates over a list of vocation data and creates `Vocation`
    objects in the database.

    Parameters
    ----------
    vocations_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for vocation_data in vocations_data:
        vocation_exists = Vocation.objects.filter(
            title=vocation_data["title"],
        ).exists()

        if not vocation_exists:
            Vocation.objects.create(
                title=vocation_data["title"],
                description=vocation_data["description"],
                author=Profile.objects.first(),
            )
