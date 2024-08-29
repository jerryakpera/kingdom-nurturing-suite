"""
Models for managing skills and interests in the profiles app.

This module defines the `Skill`, `ProfileSkill`, and `ProfileInterest`
models. These models allow for the management of skills and interests
associated with user profiles, ensuring that a profile cannot have the
same skill listed as both a skill and an interest.
"""

from uuid import uuid4

from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from django.db import models
from tinymce import models as tinymce_models

from kns.core.modelmixins import TimestampedModel
from kns.profiles.models import Profile


class Skill(TimestampedModel, models.Model):
    """
    Model representing a skill.

    Each skill has a title, a slug generated from a UUID, content in HTML,
    an author (a profile), and an optional image. The combination of the
    title and slug is unique.
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
        related_name="skills_created",
        on_delete=models.CASCADE,
    )
    image = CloudinaryField(
        null=True,
        blank=True,
        folder="kns/images/skills/",
    )

    class Meta:
        unique_together = ("title", "slug")

    def __str__(self) -> str:
        """
        Return a string representation of the Skill instance.

        Returns
        -------
        str
            The title of the skill.
        """
        return self.title


class ProfileSkill(TimestampedModel, models.Model):
    """
    Model representing a skill associated with a profile.

    This model links a profile with a specific skill. The `clean` method
    ensures that the same skill cannot be listed as both a skill and an
    interest for the same profile.
    """

    profile = models.ForeignKey(
        Profile,
        related_name="skills",
        on_delete=models.CASCADE,
    )
    skill = models.ForeignKey(
        Skill,
        related_name="skilled_profiles",
        on_delete=models.CASCADE,
    )

    def clean(self):
        """
        Custom validation to ensure that a skill cannot be listed as
        both a skill and an interest for the same profile.
        """
        if ProfileInterest.objects.filter(
            profile=self.profile,
            interest=self.skill,
        ).exists():
            raise ValidationError(
                (
                    f"The skill '{self.skill.title}' is already listed "
                    "as an interest for this profile."
                )
            )

    def __str__(self) -> str:
        """
        Return a string representation of the ProfileSkill instance.

        Returns
        -------
        str
            A string combining the profile's full name and the skill title.
        """
        return f"{self.profile.get_full_name()} - {self.skill.title}"

    class Meta:
        unique_together = ("profile", "skill")


class ProfileInterest(TimestampedModel, models.Model):
    """
    Model representing an interest associated with a profile.

    This model links a profile with a specific interest (which is a skill).
    The `clean` method ensures that the same interest cannot be listed as
    both an interest and a skill for the same profile.
    """

    profile = models.ForeignKey(
        Profile,
        related_name="interests",
        on_delete=models.CASCADE,
    )
    interest = models.ForeignKey(
        Skill,
        related_name="interested_profiles",
        on_delete=models.CASCADE,
    )

    def clean(self):
        """
        Custom validation to ensure that an interest cannot be listed as
        both an interest and a skill for the same profile.
        """
        if ProfileSkill.objects.filter(
            profile=self.profile,
            skill=self.interest,
        ).exists():
            raise ValidationError(
                (
                    f"The interest '{self.interest.title}' is already "
                    "listed as a skill for this profile."
                )
            )

    def __str__(self) -> str:
        """
        Return a string representation of the ProfileInterest instance.

        Returns
        -------
        str
            A string combining the profile's full name and the interest title.
        """
        return f"{self.profile.get_full_name()} - {self.interest.title}"

    class Meta:
        unique_together = ("profile", "interest")
