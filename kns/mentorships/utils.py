"""
Utility functions for the `mentorships` app.
"""

from kns.profiles.models import Profile

from .models import MentorshipArea, MentorshipGoal


def populate_mentorship_areas(mentorship_areas_data):
    """
    Populate the database with mentorship_area data.

    This function iterates over a list of mentorship_area data and
    creates `MentorshipArea` objects in the database.

    Parameters
    ----------
    mentorship_areas_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for mentorship_area_data in mentorship_areas_data:
        mentorship_area_exists = MentorshipArea.objects.filter(
            title=mentorship_area_data["title"],
        ).exists()

        if not mentorship_area_exists:
            MentorshipArea.objects.create(
                title=mentorship_area_data["title"],
                content=mentorship_area_data["content"],
                author=Profile.objects.first(),
            )


def populate_mentorship_goals(mentorship_goals_data):
    """
    Populate the database with mentorship_goal data.

    This function iterates over a list of mentorship_goal data and
    creates `MentorshipGoal` objects in the database.

    Parameters
    ----------
    mentorship_goals_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for mentorship_goal_data in mentorship_goals_data:
        mentorship_goal_exists = MentorshipGoal.objects.filter(
            title=mentorship_goal_data["title"],
        ).exists()

        if not mentorship_goal_exists:
            MentorshipGoal.objects.create(
                title=mentorship_goal_data["title"],
                content=mentorship_goal_data["content"],
                author=Profile.objects.first(),
            )
