"""
Utility functions for the `movements` app.
"""

from kns.profiles.models import Profile

from .models import Movement, MovementTopic


def populate_movements(movements_data):
    """
    Populate the database with movement data.

    This function iterates over a list of movement data and creates `Movement`
    objects in the database.

    Parameters
    ----------
    movements_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for movement_data in movements_data:
        movement_exists = Movement.objects.filter(
            title=movement_data["title"],
        ).exists()

        if not movement_exists:
            Movement.objects.create(
                title=movement_data["title"],
                content=movement_data["content"],
                author=Profile.objects.first(),
            )


def populate_movement_topics(movement_topics_data):
    """
    Populate the database with movement_topic data.

    This function iterates over a list of movement_topic data and creates `MovementTopic`
    objects in the database.

    Parameters
    ----------
    movement_topics_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for movement_topic_data in movement_topics_data:
        movement_topic_exists = MovementTopic.objects.filter(
            title=movement_topic_data["title"],
        ).exists()

        if not movement_topic_exists:
            MovementTopic.objects.create(
                title=movement_topic_data["title"],
                content=movement_topic_data["content"],
                author=Profile.objects.first(),
            )
