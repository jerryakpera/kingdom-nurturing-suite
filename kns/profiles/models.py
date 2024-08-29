"""
Models for the profiles app.
"""

from datetime import datetime
from uuid import uuid4

from cloudinary.models import CloudinaryField
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
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
    # TODO: Add setting to determine if the user receives
    # email notifications

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

    def get_age(self):
        """
        Calculate and return the profile's age based on date_of_birth.

        Returns
        -------
        int
            The age of the profile instance.
        """
        return model_methods.get_age(self)

    def is_under_age(self):
        """
        Check if the profile is under the legal age.

        Returns
        -------
        bool
            True if the profile is under age, False otherwise.
        """
        from kns.core.models import Setting

        settings = Setting.get_or_create_setting()

        return model_methods.is_under_age(
            self,
            settings.adult_age,
        )

    def get_current_consent_form(self):
        """
        Get the current consent form associated with the profile.

        Returns
        -------
        ConsentForm
            The current consent form for the profile instance.
        """
        return model_methods.get_current_consent_form(self)

    def needs_consent_form(self):
        """
        Determine if the profile needs a consent form.

        Returns
        -------
        bool
            True if the profile needs a consent form, False otherwise.
        """
        if not self.is_under_age():
            return False

        try:
            # Check if a consent form exists and if it's not rejected
            consent_form = self.consent_form

            if consent_form.status == ConsentForm.PENDING:
                return True

            if consent_form.status == ConsentForm.REJECTED:
                return True

            if consent_form.status == ConsentForm.APPROVED:
                return False

        except ConsentForm.DoesNotExist:
            # There is no consent form so return True
            return True

    def can_become_leader_role(self):
        """
        Determine if the profile can become a leader role.

        Returns
        -------
        bool
            True if the profile can become a leader, False otherwise.
        """
        return model_methods.can_become_leader_role(self)

    def can_become_member_role(self):
        """
        Determine if the profile can become a member role.

        Returns
        -------
        bool
            True if the profile can become a member, False otherwise.
        """
        return model_methods.can_become_member_role(self)

    def needs_approval_to_change_group_members_role(self):  # pragma: no cover
        """
        Determine if approval is required to change the role of a group member.

        This method checks if the current member is the origin user (i.e., the
        original leader of the group without a parent group). If they are,
        no approval is required. Otherwise, it checks the settings to determine
        if approval is required for role changes within the group.

        Returns
        -------
        bool
            True if approval is required to change the role; False otherwise.
        """
        from kns.core.models import Setting

        settings = Setting.get_or_create_setting()

        is_origin_user = not hasattr(
            self.group_led,
            "parent",
        )

        if is_origin_user:
            return False

        return settings.change_role_approval_required

    def change_role_to_leader(self, leader):  # pragma: no cover
        """
        Change the role of a member to leader, with an optional approval process.

        This method updates the role of the current member to "leader".
        If approval is required, it creates an approval action instead of
        directly changing the role.

        Parameters
        ----------
        leader : Profile
            The profile of the person initiating the role change.
        """
        from kns.core import constants as core_constants
        from kns.core.models import MakeLeaderActionApproval

        approval_required = leader.needs_approval_to_change_group_members_role()

        if not approval_required:
            # Update the profile role to leader
            self.role = "leader"
            self.save()
        else:
            # Create the approval action
            MakeLeaderActionApproval.objects.create(
                new_leader=self,
                created_by=leader,
                group_created_for=leader.group_in.group,
                action_type=core_constants.CHANGE_ROLE_TO_LEADER_ACTION_TYPE,
            )

    def formatted_date_of_birth(self):
        """
        Return the formatted date of birth as a string.

        This method formats the profile's date of birth into a readable string
        format. If the date of birth is not set, it returns a placeholder string.

        Returns
        -------
        str
            The formatted date of birth or a placeholder string if the date is not set.
        """
        if self.date_of_birth:
            return self.date_of_birth.strftime("%B %d, %Y")
        else:
            return "---"

    def place_of_birth_display(self):
        """
        Return a formatted string representing the place of birth.

        This method constructs a string that includes the country and city of the
        profile's place of birth. If either the country or city is not set, it
        returns a placeholder string `"---"`.

        Returns
        -------
        str
            The formatted place of birth, or `"---"` if no place of birth information is set.
        """
        place_of_birth_str = "---"

        if self.place_of_birth_country:
            place_of_birth_str = self.place_of_birth_country.name

            if self.place_of_birth_city:
                place_of_birth_str += f", {self.place_of_birth_city}"

        return place_of_birth_str

    def location_display(self):
        """
        Return a formatted string representing the current location.

        This method constructs a string that includes the country and city of the
        profile's current location. If either the country or city is not set, it
        returns a placeholder string `"---"`.

        Returns
        -------
        str
            The formatted location, or `"---"` if no location information is set.
        """
        location_str = "---"

        if self.location_country:
            location_str = self.location_country.name

            if self.location_city:
                location_str += f", {self.location_city}"

        return location_str

    # def can_edit


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


class ConsentForm(modelmixins.TimestampedModel, models.Model):
    """
    Represents a consent form associated with a Profile.

    The `ConsentForm` model tracks consent forms that are submitted by
    users, including their status (pending, approved, or rejected) and
    details about who reviewed the form.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    ]

    profile = models.OneToOneField(
        Profile,
        related_name="consent_form",
        on_delete=models.CASCADE,
    )

    consent_form = CloudinaryField(
        null=True,
        blank=True,
        resource_type="auto",
        folder="kns/files/consent_forms/",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    submitted_by = models.ForeignKey(
        Profile,
        related_name="consent_forms_submitted",
        on_delete=models.CASCADE,
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    reviewed_by = models.ForeignKey(
        Profile,
        related_name="reviewed_consent_forms",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    reject_reason = models.TextField(
        null=True,
        blank=True,
        validators=[
            MinLengthValidator(constants.REJECT_REASON_MIN_LENGTH),
            MaxLengthValidator(constants.REJECT_REASON_MAX_LENGTH),
        ],
    )

    def __str__(self):
        """
        Return a string representation of the ConsentForm instance.

        The string includes the profile associated with the consent form and
        the current status of the consent form.

        Returns
        -------
        str
            A string representation of the ConsentForm instance, formatted
            as "{profile} consent form - {status}" where {profile} is the
            string representation of the associated Profile and {status} is
            the display name of the consent form's status.
        """

        return f"{self.profile} consent form - {self.get_status_display()}"

    def approve(self, reviewer):
        """
        Approve the consent form.

        Parameters
        ----------
        reviewer : User
            The user who reviewed and approved the consent form.
        """
        self.status = self.APPROVED

        self.reviewed_at = timezone.now()
        self.reviewed_by = reviewer

        self.save()

    def reject(self, reviewer):
        """
        Reject the consent form.

        Parameters
        ----------
        reviewer : User
            The user who reviewed and rejected the consent form.
        """
        self.status = self.REJECTED

        self.reviewed_at = timezone.now()
        self.reviewed_by = reviewer

        self.save()
