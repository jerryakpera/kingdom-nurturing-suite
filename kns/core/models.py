"""
Models for the core app.
"""

from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone

from kns.groups.models import Group
from kns.profiles.models import Profile

from . import constants
from . import emails as core_emails
from .modelmixins import TimestampedModel


class FAQ(models.Model):
    """
    Model to store Frequently Asked Questions (FAQs) related to the
    Kingdom Nurturing Suite (KNS).
    """

    class Meta:
        verbose_name_plural = "Frequently asked questions"

    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        """
        Return a string representation of an FAQ instance.

        Returns
        -------
        str
            The question of the FAQ instance.
        """
        return self.question


class Setting(models.Model):
    """
    A model representing the various settings and configurations
    used throughout the application. These settings dictate the
    limits, permissions, and defaults that guide user interactions
    and the overall behavior of the application.
    """

    adult_age = models.PositiveIntegerField(
        default=constants.DEFAULT_ADULT_AGE,
        verbose_name="Adult Age",
        help_text="The age considered as an adult in the application.",
    )
    min_registration_age = models.PositiveIntegerField(
        default=constants.MIN_REGISTRATION_AGE,
        verbose_name="Minimum Registration Age",
        help_text="The minimum age required to register in the application.",
    )
    max_mentorship_areas_per_user = models.PositiveIntegerField(
        default=constants.MAX_MENTORSHIP_AREAS_USER,
        verbose_name="Maximum Mentorship Areas Per User",
        help_text="The maximum number of mentorship areas a user can select.",
    )
    max_active_mentors_per_user = models.PositiveIntegerField(
        default=constants.MAX_MENTORS_USER,
        verbose_name="Maximum Active Mentors Per User",
        help_text="The maximum number of active mentors a user can have.",
    )
    max_active_mentees_per_user = models.PositiveIntegerField(
        default=constants.MAX_MENTEES_USER,
        verbose_name="Maximum Active Mentees Per User",
        help_text="The maximum number of active mentees a user can have.",
    )
    max_skills_per_user = models.PositiveIntegerField(
        default=constants.MAX_SKILLS_USER,
        verbose_name="Maximum Skills Per User",
        help_text="The maximum number of skills a user can add.",
    )
    max_interests_per_user = models.PositiveIntegerField(
        default=constants.MAX_INTERESTS_USER,
        verbose_name="Maximum Interests Per User",
        help_text="The maximum number of interests a user can add.",
    )
    max_goals_per_mentorship = models.PositiveIntegerField(
        default=constants.MAX_GOALS_MENTORSHIP,
        verbose_name="Maximum Goals Per Mentorship",
        help_text="The maximum number of goals that can be set for a mentorship.",
    )
    default_contact_visibility = models.BooleanField(
        default=True,
        choices=constants.BOOLEAN_CHOICES,
        verbose_name="Default Contact Visibility",
        help_text="Determines if the contact information is visible by default.",
    )
    change_role_approval_required = models.BooleanField(
        default=constants.CHANGE_ROLE_PERMISSION_REQUIRED,
        choices=constants.BOOLEAN_CHOICES,
        verbose_name="Change Role Permission Required",
        help_text="Specifies if approval is required to change a user's role.",
    )
    publish_event_approval_required = models.BooleanField(
        default=constants.PUBLISH_EVENT_PERMISSION_REQUIRED,
        choices=constants.BOOLEAN_CHOICES,
        verbose_name="Publish Event Permission Required",
        help_text="Specifies if approval is required to publish an event.",
    )
    start_mentorship_approval_required = models.BooleanField(
        default=constants.START_MENTORSHIP_PERMISSION_REQUIRED,
        choices=constants.BOOLEAN_CHOICES,
        verbose_name="Start Mentorship Permission Required",
        help_text="Specifies if approval is required to start a mentorship.",
    )
    add_group_member_approval_required = models.BooleanField(
        default=constants.ADD_GROUP_MEMBER_PERMISSION_REQUIRED,
        choices=constants.BOOLEAN_CHOICES,
        verbose_name="Add Group Member Permission Required",
        help_text="Specifies if approval is required to add a member to a group.",
    )
    publish_testimony_approval_required = models.BooleanField(
        default=constants.PUBLISH_TESTIMONY_PERMISSION_REQUIRED,
        choices=constants.BOOLEAN_CHOICES,
        verbose_name="Publish Testimony Permission Required",
        help_text="Specifies if approval is required to publish a testimony.",
    )
    publish_good_practice_approval_required = models.BooleanField(
        default=constants.PUBLISH_GOOD_PRACTICE_PERMISSION_REQUIRED,
        choices=constants.BOOLEAN_CHOICES,
        verbose_name="Publish Good Practice Permission Required",
        help_text="Specifies if approval is required to publish a good practice.",
    )
    publish_prayer_request_approval_required = models.BooleanField(
        default=constants.PUBLISH_PRAYER_REQUEST_PERMISSION_REQUIRED,
        choices=constants.BOOLEAN_CHOICES,
        verbose_name="Publish Prayer Request Permission Required",
        help_text="Specifies if approval is required to publish a prayer request.",
    )
    minimum_mentorship_duration_in_weeks = models.PositiveIntegerField(
        default=4,
        verbose_name="Minimum Mentorship Duration (Weeks)",
        help_text="The minimum duration in weeks for a mentorship.",
    )
    minimum_mentorship_duration_in_weeks_description = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Minimum Mentorship Duration Description",
        help_text="Description of the minimum mentorship duration.",
    )
    max_mentorship_duration_weeks = models.PositiveIntegerField(
        default=constants.MAX_MENTORSHIP_DURATION_WEEKS,
        verbose_name="Maximum Mentorship Duration (Weeks)",
        help_text="The maximum duration in weeks for a mentorship.",
    )
    min_mentorship_duration_weeks = models.PositiveIntegerField(
        default=constants.MIN_MENTORSHIP_DURATION_WEEKS,
        verbose_name="Minimum Mentorship Duration (Weeks)",
        help_text="The minimum duration in weeks for a mentorship.",
    )
    mentorship_prohibition_period_weeks = models.PositiveIntegerField(
        default=constants.MENTORSHIP_PROHIBITION_WEEKS,
        verbose_name="Mentorship Prohibition Period (Weeks)",
        help_text="The prohibition period in weeks before starting a new mentorship.",
    )
    default_event_registration_limit = models.PositiveIntegerField(
        default=constants.EVENT_REGISTRATION_LIMIT,
        verbose_name="Default Event Registration Limit",
        help_text="The default limit for event registrations.",
    )
    organizer_must_facilitate_training = models.BooleanField(
        default=constants.ORGANIZER_MUST_FACILITATE,
        choices=constants.BOOLEAN_CHOICES,
        verbose_name="Organizer Must Facilitate Training",
        help_text="Specifies if the organizer must facilitate training.",
    )
    min_days_to_modify_sensitive_content = models.PositiveIntegerField(
        default=constants.MIN_DAYS_TO_MODIFY_SENSITIVE_CONTENT,
        verbose_name="Minimum Days to Modify Sensitive Content",
        help_text="The minimum number of days required to modify sensitive content.",
    )
    min_skills_per_training = models.PositiveIntegerField(
        default=constants.MIN_SKILLS_TRAINING,
        verbose_name="Minimum Skills Per Training",
        help_text="The minimum number of skills required per training.",
    )
    max_skills_per_training = models.PositiveIntegerField(
        default=constants.MAX_SKILLS_TRAINING,
        verbose_name="Maximum Skills Per Training",
        help_text="The maximum number of skills allowed per training.",
    )

    def clean(self):
        """
        Custom validation logic for the Setting model.

        Ensures that the minimum mentorship duration does not exceed
        the maximum mentorship duration.
        """
        if self.min_mentorship_duration_weeks > self.max_mentorship_duration_weeks:
            raise ValidationError(
                "Minimum mentorship duration cannot exceed maximum duration.",
            )

    def save(self, *args, **kwargs):
        """
        Override the save method to ensure only one instance of
        Setting exists in the database.

        If a Setting instance already exists, it reuses its primary
        key to update the existing record instead of creating a new one.

        Parameters
        ----------
        *args
            Positional arguments passed to the save method.
        **kwargs
            Keyword arguments passed to the save method.
        """
        if Setting.objects.exists():
            existing_setting = Setting.get_or_create_setting()
            self.pk = existing_setting.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_setting(cls):
        """
        Retrieve the existing Setting instance or creates a new one if none exists.

        Returns
        -------
        Setting
            The existing or newly created Setting instance.
        """
        try:
            return cls.objects.get(pk=1)
        except ObjectDoesNotExist:
            setting = cls.objects.create()
            return setting

    def __str__(self):
        """
        Return a string representation of the Setting model.

        The string representation is simply 'Settings' to indicate
        that this model stores global settings for the application.

        Returns
        -------
        str
            The string 'Settings'.
        """
        return "Settings"

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"
        """
        Meta options for the Setting model.

        Provides human-readable names for the model and its plural form.
        """


class ActionApproval(TimestampedModel, models.Model):  # pragma: no cover
    """
    Model representing an action that requires approval from a leader.
    """

    class Meta:
        abstract = True

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
    ]

    ACTION_TYPE_CHOICES = [
        (
            constants.CHANGE_ROLE_TO_LEADER_ACTION_TYPE,
            "Change role to leader",
        ),
    ]

    created_by = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="initiated_approvals",
    )

    group_created_for = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="approval_requests",
    )

    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPE_CHOICES,
        default="change_role_to_leader",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
    )

    approved_by = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_actions",
    )

    read_by = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="approved_actions_read",
    )

    timeout_duration = models.DurationField(
        default=timedelta(days=7),
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def check_timeout(self):  # pragma: no cover
        """
        Check if the approval request has timed out.
        """
        if (
            self.status == "pending"
            and (self.created_at + self.timeout_duration) < timezone.now()
        ):
            self.status = "expired"

            self.save()
            self.notify_approval()


class MakeLeaderActionApproval(ActionApproval):  # pragma: no cover
    """
    Specialized action approval for making a profile a leader.
    """

    new_leader = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="make_leader_action_approvals",
    )

    def notify_consumer(self, request):
        """
        Notify the new leader of the approval request.

        This method sends a notification to the individual group leader
        about the approval request for a role change initiated by a specific user.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object, used to retrieve the current site
            domain and other request-specific data.
        """
        core_emails.send_make_leader_action_approval_consumer_email(
            request,
            self,
            self.new_leader,
            self.created_by,
            self.group_created_for.leader,
        )

    def approve(self, consumer):
        """
        Approve the action request.

        This method sets the status to 'approved', records the approver,
        and sets the approved_at timestamp to the current time.

        Parameters
        ----------
        consumer : Profile
            The leader or admin that is approving the action.
        """
        if self.status == "pending":
            self.approved_by = consumer
            self.status = "approved"
            self.approved_at = timezone.now()
            self.new_leader.role = "leader"
            self.new_leader.save()
            self.save()

    def __str__(self):
        """
        Return a human-readable string representation of the approval action.

        This method returns a string combining the action type and the full
        name of the new leader, providing a clear and concise representation
        of the action for display purposes.

        Returns
        -------
        str
            A string representing the action type and the new leader's
            full name.
        """
        return f"{self.get_action_type_display()} ({self.new_leader.get_full_name()})"
