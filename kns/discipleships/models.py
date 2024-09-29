"""
Models for the `discipleships` app.
"""

from uuid import uuid4

from django.db import models

from kns.core import modelmixins
from kns.profiles.models import Profile

from . import constants


class Discipleship(
    modelmixins.TimestampedModel,
    models.Model,
):
    """
    Represents a discipleship relationship between two profiles.
    """

    class Meta:
        ordering = ("-created_at",)
        # Other Meta options, if any

    disciple = models.ForeignKey(
        Profile,
        related_name="discipleships_where_disciple",
        on_delete=models.CASCADE,
        help_text="The profile being discipled.",
    )

    discipler = models.ForeignKey(
        Profile,
        related_name="discipleships_where_discipler",
        on_delete=models.CASCADE,
        help_text="The profile acting as the discipler.",
    )

    group = models.CharField(
        max_length=12,
        choices=constants.DISCIPLESHIP_GROUP_CHOICES,
        default="group_member",
        help_text=(
            "The group classification of the discipleship (e.g., "
            "group_member, group_leader)."
        ),
    )

    author = models.ForeignKey(
        Profile,
        related_name="discipleships_created",
        on_delete=models.CASCADE,
        help_text="The profile that created this discipleship relationship.",
    )

    slug = models.SlugField(
        unique=True,
        default=uuid4,
        null=True,
        blank=True,
        editable=False,
        help_text="A unique identifier for the discipleship instance.",
    )

    def __str__(self) -> str:
        """
        Return a string representation of the Discipleship instance.

        Returns
        -------
        str
            A string showing the group, disciple, and discipler in this
            relationship.
        """
        return f"{self.group} discipleship of {self.disciple} by {self.discipler}"

    def group_display(self) -> str:
        """
        Return a human-readable string representation of the group.

        Returns
        -------
        str
            A string representing the group classification.
        """
        groups_key = {
            "group_member": "Group member",
            "first_12": "First 12",
            "first_3": "First 3",
            "sent_forth": "Sent forth",
        }

        return groups_key[self.group]
