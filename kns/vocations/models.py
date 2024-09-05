"""
Models for the `vocations` app.
"""

from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.urls import reverse

from kns.core.modelmixins import TimestampedModel
from kns.profiles.models import Profile


class Vocation(
    TimestampedModel,
    models.Model,
):
    """
    A model representing a vocation, which is created by a profile (author) and
    includes a title and description. Inherits timestamp and status functionality
    from mixins.

    Attributes
    ----------
    title : str
        The unique title of the vocation.
    description : str
        A text description of the vocation.
    author : Profile
        The profile that created the vocation.
    """

    title = models.CharField(
        max_length=250,
        unique=True,
        validators=[
            MinLengthValidator(3),
            RegexValidator(
                regex=r"^\S.*\S$",
                message="Title must not have leading or trailing spaces.",
            ),
        ],
    )
    description = models.TextField(blank=False)
    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="vocations_created",
    )

    class Meta:
        verbose_name = "Vocation"
        verbose_name_plural = "Vocations"
        indexes = [models.Index(fields=["title"])]

    def __str__(self):
        """
        Return the string representation of the Vocation.

        Returns
        -------
        str
            The title of the vocation.
        """
        return self.title

    def __repr__(self):
        """
        Return the official string representation of the Vocation.

        Returns
        -------
        str
            A string representing the Vocation with its title and author username.
        """
        return f"<Vocation(title={self.title}, author={self.author.user.username})>"

    def get_absolute_url(self):
        """
        Get the URL for the detailed view of the Vocation.

        Returns
        -------
        str
            The URL for the vocation_detail view.
        """
        return reverse("vocations:vocation_detail", args=[str(self.id)])


class ProfileVocation(TimestampedModel, models.Model):
    """
    A model representing the many-to-many relationship between profiles
    and vocations. Each profile can have multiple vocations, and each
    vocation can be assigned to multiple profiles.

    Attributes
    ----------
    profile : Profile
        The profile to which the vocation is assigned.
    vocation : Vocation
        The assigned vocation.
    """

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="vocations",
    )

    vocation = models.ForeignKey(
        Vocation,
        on_delete=models.CASCADE,
        related_name="profiles",
    )

    class Meta:
        verbose_name = "Profile Vocation"
        verbose_name_plural = "Profile Vocations"
        unique_together = ("profile", "vocation")

    def __str__(self):
        """
        Return the string representation of the ProfileVocation.

        Returns
        -------
        str
            A string combining the full name of the profile and the title of the vocation.
        """
        return f"{self.profile.get_full_name()} - {self.vocation.title}"
