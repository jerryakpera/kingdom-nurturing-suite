"""
Models for the `faith_milestones` app.

This module contains models representing milestones that can be achieved by
profiles and groups within the Kingdom Nurturing Suite (KNS) project.
"""

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from kns.core.modelmixins import TimestampedModel
from kns.groups.models import Group
from kns.profiles.models import Profile

from . import constants as group_constants


class FaithMilestone(TimestampedModel, models.Model):
    """
    Model representing a faith milestone that can be achieved by a profile
    or group.

    Attributes
    ----------
    title : str
        The title of the milestone.
    description : str
        A detailed description of the milestone.
    type : str
        The type of milestone, either 'profile' or 'group'.
    author : Profile
        The profile that authored or created the milestone.
    """

    title = models.CharField(max_length=255)

    description = models.TextField(
        validators=[
            MinLengthValidator(
                group_constants.MIN_MILESTONE_DESCRIPTION_LENGTH,
            ),
            MaxLengthValidator(
                group_constants.MAX_MILESTONE_DESCRIPTION_LENGTH,
            ),
        ]
    )

    type = models.CharField(
        max_length=10,
        choices=group_constants.MILESTONE_TYPE_CHOICES,
        default="profile",
    )

    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="created_faith_milestones",
    )

    def __str__(self):
        """
        Return a string representation of the FaithMilestone instance.

        Returns
        -------
        str
            The title of the milestone.
        """
        return self.title


class ProfileFaithMilestone(TimestampedModel, models.Model):
    """
    Model representing the association between a profile and a faith milestone.

    Attributes
    ----------
    profile : Profile
        The profile associated with the faith milestone.
    faith_milestone : FaithMilestone
        The faith milestone associated with the profile.
    """

    profile = models.ForeignKey(
        Profile,
        related_name="faith_milestones",
        on_delete=models.CASCADE,
    )

    faith_milestone = models.ForeignKey(
        FaithMilestone,
        related_name="profiles",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of the ProfileFaithMilestone instance.

        Returns
        -------
        str
            A string combining the profile's full name and the faith milestone's title.
        """
        return f"{self.profile.get_full_name()} - {self.faith_milestone.title}"

    class Meta:
        """
        Meta options for the ProfileFaithMilestone model.
        """

        unique_together = ("profile", "faith_milestone")


class GroupFaithMilestone(TimestampedModel, models.Model):
    """
    Model representing the association between a group and a faith milestone.

    Attributes
    ----------
    group : Group
        The group associated with the faith milestone.
    faith_milestone : FaithMilestone
        The faith milestone associated with the group.
    """

    group = models.ForeignKey(
        Group,
        related_name="faith_milestones",
        on_delete=models.CASCADE,
    )

    faith_milestone = models.ForeignKey(
        FaithMilestone,
        related_name="groups",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of the GroupFaithMilestone instance.

        Returns
        -------
        str
            A string combining the group's name and the faith milestone's title.
        """
        return f"{self.group} - {self.faith_milestone.title}"

    class Meta:
        """
        Meta options for the GroupFaithMilestone model.
        """

        unique_together = ("group", "faith_milestone")
