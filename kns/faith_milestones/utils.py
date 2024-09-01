"""
This module provides a utility function to populate the database with
faith milestone data.
"""

from kns.profiles.models import Profile

from .models import FaithMilestone


def populate_faith_milestones(faith_milestones_data):
    """
    Populate the database with faith milestone data.

    This function iterates over a list of faith milestone data and
    creates `FaithMilestone` objects in the database.

    Parameters
    ----------
    faith_milestones_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for faith_milestone_data in faith_milestones_data:
        faith_milestone_exists = FaithMilestone.objects.filter(
            title=faith_milestone_data["title"],
        ).exists()

        if not faith_milestone_exists:
            FaithMilestone.objects.create(
                type=faith_milestone_data["type"],
                title=faith_milestone_data["title"],
                description=faith_milestone_data["description"],
                author=Profile.objects.first(),
            )
