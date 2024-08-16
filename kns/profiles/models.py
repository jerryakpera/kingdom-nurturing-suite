"""
Models for the profiles app.
"""

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    role = models.CharField(
        max_length=20,
        choices=PROFILE_ROLE_OPTIONS,
        default="member",
    )

    verified = models.BooleanField(default=False)
    is_visitor = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=False)

    email = models.EmailField(
        unique=True,
        default="default@email.kns",
    )
    # last_name = models.CharField(
    #     max_length=25,
    #     null=True,
    #     blank=True,
    # )
    # first_name = models.CharField(
    #     max_length=25,
    #     null=True,
    #     blank=True,
    # )
    # gender = models.CharField(
    #     max_length=6,
    #     choices=GENDER_OPTIONS,
    #     null=True,
    #     blank=True,
    # )

    # date_of_birth = models.CharField(
    #     null=True,
    #     blank=True,
    # )


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
