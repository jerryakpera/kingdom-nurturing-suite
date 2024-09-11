"""
Models for the `classifications` app.
"""

from uuid import uuid4

from django.db import models
from tinymce import models as tinymce_models

from kns.core.modelmixins import TimestampedModel
from kns.profiles.models import Profile


class Classification(
    TimestampedModel,
    models.Model,
):
    """
    Model representing a Classification within the system. Classifications
    are unique entities with content, a title, an author, and a defined order.

    Attributes
    ----------
    title : str
        The title of the classification.
    slug : UUID
        A unique identifier generated for the classification.
    content : HTMLField
        The main content of the classification, stored as HTML.
    order : int
        The order in which this classification appears.
    author : Profile
        The profile that created the classification.
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
    order = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        unique=True,
    )
    author = models.ForeignKey(
        Profile,
        related_name="classifications_created",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of a Classification instance.

        Returns
        -------
        str
            The title of the classification.
        """
        return self.title

    class Meta:
        ordering = ("order",)
        unique_together = ("title", "slug")


class Subclassification(
    TimestampedModel,
    models.Model,
):
    """
    Model representing a Subclassification, which is linked to a Classification.
    Subclassifications have content, titles, and an author like Classifications.

    Attributes
    ----------
    title : str
        The title of the subclassification.
    slug : UUID
        A unique identifier generated for the subclassification.
    content : HTMLField
        The main content of the subclassification, stored as HTML.
    author : Profile
        The author (profile) who created the subclassification.
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
        related_name="subclassifications_created",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of a Subclassification instance.

        Returns
        -------
        str
            The title of the subclassification.
        """
        return self.title

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("title", "slug")


class ClassificationSubclassification(models.Model):
    """
    Model representing the many-to-many relationship between Classifications
    and Subclassifications. Each Classification can have multiple
    Subclassifications, and each Subclassification can belong to multiple
    Classifications.

    Attributes
    ----------
    classification : ForeignKey
        The Classification to which the subclassification belongs.
    subclassification : ForeignKey
        The Subclassification linked to the classification.
    """

    class Meta:
        unique_together = (
            "classification",
            "subclassification",
        )

    classification = models.ForeignKey(
        Classification,
        related_name="classification_subclassifications",
        on_delete=models.CASCADE,
    )
    subclassification = models.ForeignKey(
        Subclassification,
        related_name="subclassification_classifications",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of a ClassificationSubclassification instance.

        Returns
        -------
        str
            The classification and subclassification titles formatted as a string.
        """
        return f"{self.classification.title} ({self.subclassification.title})"


class ProfileClassification(TimestampedModel, models.Model):
    """
    Model representing a classification of a profile, with optional subclassification.

    Attributes
    ----------
    no : int
        The identification number for the profile classification.
    profile : ForeignKey
        A reference to the profile associated with this classification.
    classification : ForeignKey
        A reference to the classification associated with the profile.
    subclassification : ForeignKey
        An optional reference to the subclassification associated with the profile.
    removed_at : DateField
        A date field indicating when the profile classification was removed.
    """

    no = models.IntegerField()
    profile = models.ForeignKey(
        Profile,
        related_name="profile_classifications",
        on_delete=models.CASCADE,
    )
    classification = models.ForeignKey(
        Classification,
        related_name="classification_profiles",
        on_delete=models.CASCADE,
    )
    subclassification = models.ForeignKey(
        Subclassification,
        related_name="subclassification_profiles",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    removed_at = models.DateField(
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        """
        Return a string representation of a ProfileClassification instance.

        If the subclassification is present, it should be included in the string output.

        Returns
        -------
        str
            A string in the format 'Full Name - Classification (Subclassification)'
            or 'Full Name - Classification' if no subclassification is present.
        """
        full_name = self.profile.get_full_name()  # Explicitly call get_full_name
        if self.subclassification:
            return f"{full_name} - {self.classification.title} ({self.subclassification.title})"

        return f"{full_name} - {self.classification.title}"
