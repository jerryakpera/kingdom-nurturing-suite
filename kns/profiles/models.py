"""
Models for the profiles app.
"""

from uuid import uuid4

from cloudinary.models import CloudinaryField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField

from kns.core import modelmixins
from kns.custom_user.models import User

from . import constants
from . import methods as model_methods


class Profile(
    modelmixins.TimestampedModel,
    modelmixins.ModelWithLocation,
    models.Model,
):
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
        choices=constants.PROFILE_ROLE_OPTIONS,
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
        choices=constants.GENDER_OPTIONS,
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
    email_notifications = models.BooleanField(
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

    def __str__(self):
        """
        Return the full name of the profile as string representation.

        Returns
        -------
        str
            The first and last name of the profile instance.
        """
        return f"{self.get_full_name()}"

    def get_full_name(self):
        """
        Return the full name of the profile instance.

        This method uses the `get_full_name` function from
        `model_methods` to generate the full name.

        Returns
        -------
        str
            The full name of the profile instance.
        """
        return model_methods.get_full_name(self)

    def is_leading_group(self):
        """
        Check if the profile is leading a group.

        This method uses the `is_leading_group` function from
        `model_methods` to determine if the profile is leading any group.

        Returns
        -------
        bool
            True if the profile is leading a group, False otherwise.
        """
        return model_methods.is_leading_group(self)

    def get_absolute_url(self):
        """
        Get the absolute URL for the profile's detail view.

        This method uses the `get_absolute_url` function from
        `model_methods` to generate the URL for the profile's detail
        view.

        Returns
        -------
        str
            The absolute URL for the profile's detail view.
        """
        return model_methods.get_absolute_url(self)

    def get_involvements_url(self):
        """
        Get the URL for the profile's involvements view.

        This method uses the `get_involvements_url` function from
        `model_methods` to generate the URL for the profile's
        involvements view.

        Returns
        -------
        str
            The URL for the profile's involvements view.
        """
        return model_methods.get_involvements_url(self)

    def get_trainings_url(self):
        """
        Get the URL for the profile's trainings view.

        This method uses the `get_trainings_url` function from
        `model_methods` to generate the URL for the profile's trainings
        view.

        Returns
        -------
        str
            The URL for the profile's trainings view.
        """
        return model_methods.get_trainings_url(self)

    def get_activities_url(self):
        """
        Get the URL for the profile's activities view.

        This method uses the `get_activities_url` function from
        `model_methods` to generate the URL for the profile's activities
        view.

        Returns
        -------
        str
            The URL for the profile's activities view.
        """
        return model_methods.get_activities_url(self)

    def get_settings_url(self):
        """
        Get the URL for the profile's settings view.

        This method uses the `get_settings_url` function from
        `model_methods` to generate the URL for the profile's settings
        view.

        Returns
        -------
        str
            The URL for the profile's settings view.
        """
        return model_methods.get_settings_url(self)

    def get_role_display_str(self):
        """
        Get the display string for the profile's role.

        This method uses the `get_role_display_str` function from
        `model_methods` to generate the display string for the profile's
        role.

        Returns
        -------
        str
            The display string for the profile's role.
        """
        return model_methods.get_role_display_str(self)

    def is_eligible_to_register_group(self):
        """
        Determine if the profile is eligible to register a new group.

        This method uses the `is_eligible_to_register_group` function
        from `model_methods` to check if the profile meets all criteria
        for registering a new group.

        Returns
        -------
        bool
            True if the profile is eligible to register a new group,
            False otherwise.
        """
        return model_methods.is_eligible_to_register_group(self)

    def is_profile_complete(self):
        """
        Check if the profile is fully completed.

        This method uses the `is_profile_complete` function from
        `model_methods` to determine if the profile is complete.

        Returns
        -------
        bool
            True if the profile is fully completed, False otherwise.
        """
        return model_methods.is_profile_complete(self)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a Profile instance when a User instance
    is created.

    This function is triggered by the `post_save` signal from the
    `User` model.
    It ensures that a corresponding `Profile` instance is created with
    the default     email if the user was just created (i.e.,
    `created` is True).

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
        such as `update_fields` or `raw` (usually not used in this
        function).
    """
    if created:
        Profile.objects.create(
            user=instance,
            email=instance.email,
        )
