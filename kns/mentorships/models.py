"""
Models for the `mentorships` app.
"""

from datetime import timedelta
from uuid import uuid4

from django.db import models
from django.utils import timezone
from tinymce import models as tinymce_models

from kns.core.constants import MENTORSHIP_GOAL_TYPES, MENTORSHIP_STATUS_CHOICES
from kns.core.modelmixins import ModelWithStatus, TimestampedModel
from kns.profiles.models import Profile


class MentorshipArea(
    TimestampedModel,
    ModelWithStatus,
    models.Model,
):
    """
    A model representing an area of mentorship.

    The `MentorshipArea` model stores information about a specific area in which
    mentorship is offered. It includes fields for the title, slug, content,
    and the author (profile) who created the mentorship area. The model also
    inherits timestamp fields for tracking creation and modification times,
    and a status field for indicating the current state of the mentorship area.

    Methods
    -------
    __str__():
        Return the title of the mentorship area, providing a string
        representation of the object.
    """

    title = models.CharField(
        max_length=150,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        default=uuid4,
        null=True,
        blank=True,
        editable=False,
    )
    content = tinymce_models.HTMLField()
    author = models.ForeignKey(
        Profile,
        related_name="mentorship_areas_created",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of the MentorshipArea instance.

        This method returns the title of the mentorship area, which is used
        to represent the object in a readable form, such as in Django admin
        or when the object is printed.

        Returns
        -------
        str
            The title of the mentorship area.
        """

        return self.title


class MentorshipGoal(
    TimestampedModel,
    ModelWithStatus,
    models.Model,
):
    """
    A model representing a mentorship goal.

    The `MentorshipGoal` model stores information about specific goals for
    mentorship. It includes fields for the title, slug, content, the author
    (profile) who created the goal, and the type of the goal. The model also
    inherits timestamp fields for tracking creation and modification times,
    and a status field for indicating the current state of the mentorship goal.

    Methods
    -------
    __str__():
        Return the title of the mentorship goal, providing a string
        representation of the object.
    """

    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(
        unique=True,
        default=uuid4,
        null=True,
        blank=True,
        editable=False,
    )
    content = tinymce_models.HTMLField()
    author = models.ForeignKey(
        Profile,
        related_name="mentorship_goalss_created",
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        max_length=30,
        choices=MENTORSHIP_GOAL_TYPES,
        default="primary",
    )

    def __str__(self) -> str:
        """
        Return a string representation of the MentorshipGoal instance.

        This method returns the title of the mentorship goal, which is used
        to represent the object in a readable form, such as in Django admin
        or when the object is printed.

        Returns
        -------
        str
            The title of the mentorship goal.
        """

        return self.title
