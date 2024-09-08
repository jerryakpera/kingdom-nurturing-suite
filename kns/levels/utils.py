"""
Utility functions for the `levels` app.
"""

from kns.profiles.models import Profile

from .models import Level, Sublevel


def populate_levels(levels_data):
    """
    Populate the database with level data.

    This function iterates over a list of level data and creates `Level`
    objects in the database.

    Parameters
    ----------
    levels_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for level_data in levels_data:
        level_exists = Level.objects.filter(
            title=level_data["title"],
        ).exists()

        if not level_exists:
            Level.objects.create(
                title=level_data["title"],
                content=level_data["content"],
                author=Profile.objects.first(),
            )


def populate_sublevels(sublevels_data):
    """
    Populate the database with sublevel data.

    This function iterates over a list of sublevel data and creates `Sublevel`
    objects in the database.

    Parameters
    ----------
    sublevels_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for sublevel_data in sublevels_data:
        sublevel_exists = Sublevel.objects.filter(
            title=sublevel_data["title"],
        ).exists()

        if not sublevel_exists:
            Sublevel.objects.create(
                title=sublevel_data["title"],
                content=sublevel_data["content"],
                author=Profile.objects.first(),
            )
