"""
Utility functions for the `classifications` app.
"""

from kns.profiles.models import Profile

from .models import Classification, Subclassification


def populate_classifications(classifications_data):
    """
    Populate the database with classification data.

    This function iterates over a list of classification data and
    creates `Classification` objects in the database.

    Parameters
    ----------
    classifications_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for classification_data in classifications_data:
        classification_exists = Classification.objects.filter(
            title=classification_data["title"],
        ).exists()

        if not classification_exists:
            Classification.objects.create(
                title=classification_data["title"],
                content=classification_data["content"],
                order=classification_data["order"],
                author=Profile.objects.first(),
            )


def populate_subclassifications(subclassifications_data):
    """
    Populate the database with subclassification data.

    This function iterates over a list of subclassification data and
    creates `Subclassification` objects in the database.

    Parameters
    ----------
    subclassifications_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for subclassification_data in subclassifications_data:
        subclassification_exists = Subclassification.objects.filter(
            title=subclassification_data["title"],
        ).exists()

        if not subclassification_exists:
            Subclassification.objects.create(
                title=subclassification_data["title"],
                content=subclassification_data["content"],
                author=Profile.objects.first(),
            )
