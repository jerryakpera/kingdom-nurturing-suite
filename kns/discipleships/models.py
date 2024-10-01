"""
Models for the `discipleships` app.
"""

from datetime import timedelta
from uuid import uuid4

from django.db import models
from django.utils import timezone

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

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date and time when the discipleship program was completed.",
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

    def running_time(self):
        """
        Calculate the running time of the discipleship in months and weeks.

        Returns
        -------
        str
            A string indicating the number of months and weeks the discipleship has been running.
        """
        # Get the end date for calculation (completed_at or now)
        end_date = self.completed_at or timezone.now()

        # Calculate the total duration
        duration = end_date - self.created_at

        # Calculate months and remaining weeks
        total_months = duration.days // 30
        remaining_days = duration.days % 30
        total_weeks = remaining_days // 7

        # Construct the output string
        result = []
        if total_months:
            result.append(f"{total_months} month{'s' if total_months > 1 else ''}")
        if total_weeks:
            result.append(f"{total_weeks} week{'s' if total_weeks > 1 else ''}")

        return " and ".join(result) if result else "less than a week"

    def total_running_time(self):
        """
        Calculate the running time of the first discipleship between the
        discipler and disciple and handle the case where 'sent_forth'
        group should stop the running time.

        Returns
        -------
        str
            A string indicating the number of months and weeks the
            discipleship has been running.
        """
        # Retrieve all discipleships between the same discipler and disciple, ordered by created_at
        discipleships = Discipleship.objects.filter(
            disciple=self.disciple, discipler=self.discipler
        ).order_by("created_at")

        # Get the first discipleship's creation date
        first_discipleship_date = discipleships.first().created_at

        # Check if there is a 'sent_forth' group discipleship
        sent_forth_discipleship = discipleships.filter(group="sent_forth").first()
        if sent_forth_discipleship:
            end_date = sent_forth_discipleship.created_at
        else:
            # If no 'sent_forth' discipleship, use the current time
            # or the completed_at date
            end_date = self.completed_at or timezone.now()

        # Calculate the total duration
        duration = end_date - first_discipleship_date

        # Calculate months and remaining weeks
        total_months = duration.days // 30
        remaining_days = duration.days % 30
        total_weeks = remaining_days // 7

        # Construct the output string
        result = []
        if total_months:
            result.append(f"{total_months} month{'s' if total_months > 1 else ''}")
        if total_weeks:
            result.append(f"{total_weeks} week{'s' if total_weeks > 1 else ''}")

        return " and ".join(result) if result else "less than a week"
