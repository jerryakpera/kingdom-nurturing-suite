"""
Models for the profiles app.
"""

from uuid import uuid4

from cloudinary.models import CloudinaryField
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField

from kns.core import modelmixins
from kns.custom_user.models import User

from . import constants, emails
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

    is_onboarded = models.BooleanField(
        default=False,
        choices=constants.BOOLEAN_CHOICES,
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

    set_password_token = models.CharField(
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
        try:
            profile_encryption = self.encryption
            return f"{profile_encryption.first_name} {profile_encryption.last_name}"
        except ProfileEncryption.DoesNotExist:
            return f"{self.first_name} {self.last_name}"

    def get_real_name(self):
        """
        Return the real name of the profile instance.

        Returns
        -------
        str
            The real name of the profile instance.
        """
        return f"{self.first_name} {self.last_name}"

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

    def get_mentorships_url(self):
        """
        Get the URL for the profile's mentorships view.

        This method uses the `get_mentorships_url` function from
        `model_methods` to generate the URL for the profile's mentorships
        view.

        Returns
        -------
        str
            The URL for the profile's mentorships view.
        """
        return model_methods.get_mentorships_url(self)

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

    def get_discipleships_url(self):
        """
        Get the URL for the profile's discipleships view.

        This method uses the `get_discipleships_url` function from
        `model_methods` to generate the URL for the profile's discipleships
        view.

        Returns
        -------
        str
            The URL for the profile's discipleships view.
        """
        return model_methods.get_discipleships_url(self)

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

    def can_become_external_person_role(self):
        """
        Determine if the profile can become an external person role.

        Returns
        -------
        bool
            True if the profile can become an external person, False otherwise.
        """
        return model_methods.can_become_external_person_role(self)

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

        if not self.group_led.parent:
            return False

        settings = Setting.get_or_create_setting()
        return settings.change_role_approval_required

    def change_role_to_leader(self):
        """
        Change the role of a profile to leader.
        """
        # Update the profile role to leader
        # TODO: Send notification email to user that their role has been changed
        # TODO: Send in app notification that their role has been changed
        self.role = "leader"
        self.save()

    def change_role_to_member(self):
        """
        Change the role of a profile to leader.
        """
        # Update the profile role to member
        # TODO: Send notification email to user that their role has been changed
        self.role = "member"
        self.save()

    def change_role_to_external_person(self):
        """
        Change the role of a profile to `external_person`.
        """
        # Update the profile role to member
        # TODO: Send notification email to user that their role has been changed
        self.role = "external_person"
        self.save()

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

    def phone_display(self):
        """
        Return a formatted string representing the current phone.

        Returns
        -------
        str
            The formatted phone, or `"---"` if no phone information is set.
        """
        phone_str = "---"

        if self.phone:
            phone_str = f"(+{self.phone_prefix}) {self.phone}"

        return phone_str

    def get_vocations_as_string(self):
        """
        Return the profile's vocations as a comma-separated string.

        This method fetches all vocations related to the profile and returns
        them as a string separated by commas.

        Returns
        -------
        str
            The vocations related to the profile as a comma-separated string.
            If no vocations are assigned, it returns 'No vocations'.
        """
        profile_vocations = self.vocations.all()

        if profile_vocations.exists():
            return ", ".join(
                profile_vocation.vocation.title
                for profile_vocation in profile_vocations
            )

        return "No vocations"

    def current_level(self):  # pragma: no cover
        """
        Return the most recent profile level for the profile.

        This method fetches all profile levels associated with the profile,
        sorts them by their creation timestamp in descending order, and returns
        the most recent one. If there are no profile levels associated, it
        returns None.

        Returns
        -------
        ProfileLevel or None
            The most recent ProfileLevel instance if available, otherwise None.
        """
        profile_levels = self.profile_levels.all()

        if profile_levels.exists():
            most_recent_level = profile_levels.order_by(
                "-created_at",
            ).first()

            return most_recent_level
        else:
            return None

    def current_classifications(self):  # pragma: no cover
        """
        Return the most recent profile classification for the profile.

        This method fetches all profile classifications associated with the profile,
        sorts them by their creation timestamp in descending order, and returns
        the most recent one. If there are no profile classifications associated, it
        returns None.

        Returns
        -------
        ProfileClassification or None
            The most recent ProfileClassification instance if available,
            otherwise None.
        """
        if self.profile_classifications.count() == 0:
            return []

        current_classification_no = (
            self.profile_classifications.order_by(
                "-no",
            )
            .first()
            .no
        )

        return self.profile_classifications.filter(
            no=current_classification_no,
        )

    def get_mentorship_areas_as_str(self) -> str:
        """
        Return the mentorship areas for the profile as a comma-separated string.
        If the profile has no mentorship areas, return '---'.

        Returns
        -------
        str
            A comma-separated string of mentorship area titles or
            '---' if none exist.
        """
        mentorship_areas = self.mentorship_areas.all()
        if mentorship_areas.exists():
            return ", ".join([area.mentorship_area.title for area in mentorship_areas])

        return "---"

    def create_profile_completion_tasks(self):
        """
        Automatically creates profile completion tasks when a profile is onboarded.
        Tasks are created based on the profile's role and existing tasks to avoid duplicates.
        """
        from kns.onboarding.constants import TASKS
        from kns.onboarding.models import ProfileCompletion, ProfileCompletionTask

        # Ensure a ProfileCompletion entry exists for the profile
        ProfileCompletion.objects.get_or_create(profile=self)

        # Define the base tasks
        base_tasks = [
            "add_vocations_skills",
            "browse_events",
        ]

        # Add role-specific tasks
        if self.role == "leader":
            base_tasks.append("register_first_member")
            base_tasks.append("register_group")

        # Create tasks only if they do not already exist
        for task_name in base_tasks:
            task_link = ""
            task_description = TASKS[task_name]["task_description"]

            if task_name == "register_group":
                task_link = reverse("groups:register_group")

            if task_name == "register_first_member":
                task_link = reverse("profiles:register_member")

            if task_name == "add_vocations_skills":
                task_link = reverse(
                    "profiles:edit_profile_vocations",
                    kwargs={
                        "profile_slug": self.slug,
                    },
                )

            ProfileCompletionTask.objects.get_or_create(
                profile=self,
                task_name=task_name,
                task_link=task_link,
                task_description=task_description,
            )

    def check_and_complete_vocations_skills(self):
        """
        Check if the profile has all three: ProfileSkill, ProfileInterest, and ProfileVocation.
        If so, mark the 'add_vocations_skills' task as complete.
        """
        from kns.onboarding.models import ProfileCompletionTask
        from kns.skills.models import ProfileInterest, ProfileSkill
        from kns.vocations.models import ProfileVocation

        with transaction.atomic():
            has_skills = ProfileSkill.objects.filter(
                profile=self,
            ).exists()
            has_interests = ProfileInterest.objects.filter(
                profile=self,
            ).exists()
            has_vocations = ProfileVocation.objects.filter(
                profile=self,
            ).exists()

            if has_skills or has_interests or has_vocations:
                task_exists = ProfileCompletionTask.objects.filter(
                    profile=self,
                    task_name="add_vocations_skills",
                ).exists()

                if task_exists:  # pragma: no cover
                    # Get or create the 'add_vocations_skills' task and mark it as complete
                    task = ProfileCompletionTask.objects.get(
                        profile=self,
                        task_name="add_vocations_skills",
                    )

                    if not task.is_complete:
                        task.is_complete = True
                        task.save()

    def send_email_to_new_leader(self, request):  # pragma: no cover
        """
        Send an email notification to a user when their role is elevated to `leader`.
        The email is sent to inform the leader about their new role and responsibilities.

        Parameters
        ----------
        request : HttpRequest
            The current HTTP request object, containing user information.
        """
        emails.send_new_leader_email(
            request=request,
            profile=self,
            profiles_leader=request.user.profile,
        )

    def send_email_to_new_member(self, request):  # pragma: no cover
        """
        Send an email notification to a user when their role is update to `member`.

        Parameters
        ----------
        request : HttpRequest
            The current HTTP request object, containing user information.
        """
        emails.send_new_member_email(
            request=request,
            profile=self,
            profiles_leader=request.user.profile,
        )

    def send_email_to_new_external_person(self, request):  # pragma: no cover
        """
        Send an email notification to a user when their role is update
        to `external_person`.

        Parameters
        ----------
        request : HttpRequest
            The current HTTP request object, containing user information.
        """
        emails.send_new_external_person_email(
            request=request,
            profile=self,
            profiles_leader=request.user.profile,
        )


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


class EncryptionReason(
    modelmixins.TimestampedModel,
    models.Model,
):
    """
    Represents a reason for encrypting a profile's name.

    Attributes:
        title: A unique title for the encryption reason.
        slug: A unique slug for the encryption reason, automatically generated.
        description: A brief description of the encryption reason.
        author: The Profile that created this encryption reason.
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
    description = models.CharField(
        max_length=250,
    )
    author = models.ForeignKey(
        Profile,
        related_name="encryption_reasons_created",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of the EncryptionReason.

        Returns
        -------
        str
            The title of the encryption reason.
        """
        return self.title

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("title", "slug")


class ProfileEncryption(
    modelmixins.TimestampedModel,
    models.Model,
):
    """
    Represents an encryption of a profile's name, making it hidden from public view.

    Attributes:
        profile: The Profile that is encrypted.
        last_name: The encrypted last name of the profile.
        first_name: The encrypted first name of the profile.
        encryption_reason: The reason for encrypting the profile's name.
    """

    profile = models.OneToOneField(
        Profile,
        related_name="encryption",
        on_delete=models.CASCADE,
    )

    encrypted_by = models.OneToOneField(
        Profile,
        related_name="created_encryptions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    last_name = models.CharField(max_length=25)
    first_name = models.CharField(max_length=25)

    encryption_reason = models.ForeignKey(
        EncryptionReason,
        related_name="encryptions",
        on_delete=models.PROTECT,
    )

    def __str__(self) -> str:
        """
        Return a string representation of the ProfileEncryption.

        Returns
        -------
        str
            A string showing the profile's full name and the encrypted name.
        """
        return f"{self.profile.get_full_name()} encrypted as {self.first_name} {self.last_name}"
