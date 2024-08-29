"""
This module provides a utility function to populate the database with
skill data.
"""

from kns.profiles.models import Profile

from .models import Skill


def populate_skills(skills_data):
    """
    Populate the database with skill data.

    This function iterates over a list of skill data and creates `Skill`
    objects in the database.

    Parameters
    ----------
    skills_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for skill_data in skills_data:
        skill_exists = Skill.objects.filter(
            title=skill_data["title"],
        ).exists()

        if not skill_exists:
            Skill.objects.create(
                title=skill_data["title"],
                content=skill_data["content"],
                author=Profile.objects.first(),
            )
