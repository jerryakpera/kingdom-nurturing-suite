"""
Models for the `levels` app.
"""

from uuid import uuid4

from django.db import models
from tinymce import models as tinymce_models

from kns.core.modelmixins import TimestampedModel
from kns.profiles.models import Profile


class Level(
    TimestampedModel,
    models.Model,
):
    """
    Model representing a Level within the system. Levels are unique entities
    with content, a title, and an author.

    Attributes
    ----------
    title : str
        The title of the level.
    slug : UUID
        A unique identifier generated for the level.
    content : HTMLField
        The main content of the level, stored as HTML.
    author : Profile
        The author (profile) who created the level.
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
        related_name="levels_created",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of a Level instance.

        Returns
        -------
        str
            The title of the level.
        """
        return self.title

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("title", "slug")


class Sublevel(
    TimestampedModel,
    models.Model,
):
    """
    Model representing a Sublevel, which is linked to a Level. Sublevels
    have content, titles, and an author like Levels.

    Attributes
    ----------
    title : str
        The title of the sublevel.
    slug : UUID
        A unique identifier generated for the sublevel.
    content : HTMLField
        The main content of the sublevel, stored as HTML.
    author : Profile
        The author (profile) who created the sublevel.
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
        related_name="sublevels_created",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of a Sublevel instance.

        Returns
        -------
        str
            The title of the sublevel.
        """
        return self.title

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("title", "slug")


class LevelSublevel(models.Model):
    """
    Model representing the many-to-many relationship between Levels and
    Sublevels. Each Level can have multiple Sublevels, and each Sublevel can
    belong to multiple Levels.

    Attributes
    ----------
    level : ForeignKey
        The Level to which the sublevel belongs.
    sublevel : ForeignKey
        The Sublevel linked to the level.
    """

    level = models.ForeignKey(
        Level,
        related_name="sublevels",
        on_delete=models.CASCADE,
    )

    sublevel = models.ForeignKey(
        Sublevel,
        related_name="levels",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of a LevelSublevel instance.

        Returns
        -------
        str
            The level and sublevel titles formatted as a string.
        """
        return f"{self.level.title} ({self.sublevel.title})"

    class Meta:
        unique_together = ["level", "sublevel"]


class ProfileLevel(TimestampedModel, models.Model):
    """
    Model representing the relationship between a Profile and a Level/Sublevel.
    A profile can be associated with a Level and optionally with a Sublevel.

    Attributes
    ----------
    profile : ForeignKey
        The profile that is linked to a specific level and sublevel.
    level : ForeignKey
        The Level associated with the profile.
    sublevel : ForeignKey
        The Sublevel associated with the profile (optional).
    removed_at : DateField
        The date when the profile was removed from the level/sublevel.
    """

    profile = models.ForeignKey(
        Profile,
        related_name="profile_levels",
        on_delete=models.CASCADE,
    )

    level = models.ForeignKey(
        Level,
        related_name="profile_levels",
        on_delete=models.CASCADE,
        null=True,
    )

    sublevel = models.ForeignKey(
        Sublevel,
        related_name="profile_levels",
        on_delete=models.CASCADE,
        null=True,
    )

    removed_at = models.DateField(
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        """
        Return a string representation of a ProfileLevel instance.

        Returns
        -------
        str
            The profile's name and their associated level and sublevel
            (if applicable).
        """
        if self.sublevel:
            return f"{self.profile.get_full_name()} - {self.level} ({self.sublevel})"

        return f"{self.profile.get_full_name()} - {self.level.title}"
