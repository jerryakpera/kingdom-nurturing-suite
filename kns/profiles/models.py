"""
Models for the profiles app.
"""

from uuid import uuid4

from cloudinary.models import CloudinaryField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django_countries.fields import CountryField

from kns.core.modelmixins import TimestampedModel
from kns.custom_user.models import User

from .constants import GENDER_OPTIONS, PROFILE_ROLE_OPTIONS


class Profile(TimestampedModel, models.Model):
    """
    Represents a user profile in the system.
    """

    user = models.OneToOneField(
        User,
        related_name="profile",
        on_delete=models.CASCADE,
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
    )

    slug = models.SlugField(
        unique=True,
        default=uuid4,
        null=True,
        blank=True,
        editable=False,
    )

    role = models.CharField(
        max_length=20,
        choices=PROFILE_ROLE_OPTIONS,
        default="member",
    )

    email = models.EmailField(
        unique=True,
        default="default@email.kns",
    )
    last_name = models.CharField(
        max_length=25,
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        max_length=25,
        null=True,
        blank=True,
    )
    gender = models.CharField(
        max_length=6,
        choices=GENDER_OPTIONS,
        null=True,
        blank=True,
        default="male",
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    chat_is_disabled = models.BooleanField(
        default=False,
    )
    email_notificaitons = models.BooleanField(
        default=True,
    )

    display_hints = models.BooleanField(
        default=True,
    )
    bio_details_is_visible = models.BooleanField(
        default=True,
    )
    contact_details_is_visible = models.BooleanField(
        default=True,
    )

    place_of_birth_country = CountryField(
        null=True,
        blank=True,
    )
    place_of_birth_city = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
    )
    phone_prefix = models.CharField(
        max_length=5,
        null=True,
        blank=True,
    )

    is_movement_training_facilitator = models.BooleanField(
        default=False,
    )
    reason_is_not_movement_training_facilitator = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )

    is_skill_training_facilitator = models.BooleanField(
        default=False,
    )
    reason_is_not_skill_training_facilitator = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )

    is_mentor = models.BooleanField(
        default=False,
    )
    reason_is_not_mentor = models.CharField(
        max_length=500,
        null=True,
        blank=True,
    )

    chat_is_disabled = models.BooleanField(default=False)
    email_notificaitons = models.BooleanField(default=True)

    display_hints = models.BooleanField(default=True)
    bio_details_is_visible = models.BooleanField(default=True)
    contact_details_is_visible = models.BooleanField(default=True)

    email_token = models.CharField(
        max_length=250,
        null=True,
        blank=True,
    )

    image = CloudinaryField(
        null=True,
        blank=True,
        folder="kns/images/profiles/",
    )

    def get_full_name(self):
        """
        Return the full name of the profile instance.

        Returns
        -------
        str
            Full name of the profile instance.
        """
        return f"{self.first_name} {self.last_name}"

    def is_leading_group(self):
        """
        Return if the profile instance is a leader of a group.

        Returns
        -------
        bool
            True/False if profile is leading group.
        """
        try:
            if self.group_led:
                return True
        except AttributeError:
            return False

    def get_absolute_url(self):
        """
        Return the absolute URL to access a detail view of this profile.

        Returns
        -------
        str
            The absolute URL of the profile's detail view.
        """
        return reverse(
            "profiles:profile_detail",
            kwargs={
                "profile_slug": self.slug,
            },
        )

    def get_role_display_str(self):
        """
        Return the string display for this profile role.

        Returns
        -------
        str
            The str representation of the profiles role.
        """
        if self.role in ["leader", "member"]:
            return self.role.title()

        return "External Person"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a Profile instance when a User instance is created.

    This function is triggered by the `post_save` signal from the `User` model.
    It ensures that a corresponding `Profile` instance is created with the default
    email if the user was just created (i.e., `created` is True).

    Parameters
    ----------
    sender : Type[Model]
        The model class sending the signal (User).
    instance : User
        The instance of the User that was created or updated.
    created : bool
        A boolean indicating whether a new instance was created
        (`True`) or an existing instance was updated (`False`).
    **kwargs
        Additional keyword arguments passed by the signal,
        such as `update_fields` or `raw` (usually not used in this function).
    """
    if created:
        Profile.objects.create(
            user=instance,
            email=instance.email,
        )
