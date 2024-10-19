"""
Models for the `activities` app.
"""

from datetime import date
from uuid import uuid4

from cloudinary.models import CloudinaryField
from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    ValidationError,
)
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager
from tinymce import models as tinymce_models

from kns.core.modelmixins import TimestampedModel
from kns.core.models import Notification
from kns.events.models import Event
from kns.events.utils import validate_image
from kns.profiles.models import Profile

# Choices for activity type
ACTIVITY_TYPE_CHOICES = [
    ("skill_training", "Skill Training"),
    ("movement_training", "Movement Training"),
    ("community_service", "Community Service"),
    ("prayer_movement", "Prayer Movement"),
]

# Default images for activities based on activity type
ACTIVITY_DEFAULT_IMAGES = {
    "skill_training": (
        "https://res.cloudinary.com/devex/image/fetch/c_scale,f_auto,q_auto,w_720/"
        "https://lh6.googleusercontent.com/fSmAR3WZ1W4MRfhR8mmjliW_Bu5xCHd3g08lpf"
        "LvLpy_HG8RIYs3Zoybx_WGf5yXJgTWUwVT94fST9jJUAMUDyNWgfA5ezWpIDi5yuc8sViINh"
        "d9Zglh6BQUR8hB0mkZ0ABLx4-M"
    ),
    "movement_training": (
        "https://dcpi-website.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/"
        "08223438/west-africa-photo-1.webp"
    ),
    "community_service": (
        "https://images2.goabroad.com/image/upload/images2/program_content/"
        "6-1519271542.jpg"
    ),
    "prayer_movement": (
        "https://www.oikoumene.org/sites/default/files/styles/max_1200x1200/"
        "public/newsItem/PhotoByAlbinHillert_20180311_AH2_1876.jpg?itok=C2aWkXER"
    ),
}


class ActivityQuerySet(models.QuerySet):  # pragma: no cover
    """
    Custom queryset for the Activity model.
    """

    def filter_by_activity_type(self, activity_type):
        """
        Filter activities by their type.

        Parameters
        ----------
        activity_type : str
            The type of activity to filter.

        Returns
        -------
        QuerySet
            A queryset containing activities of the specified type.
        """
        return self.filter(
            activity_type=activity_type,
        )


class ActivityManager(models.Manager):  # pragma: no cover
    """
    Custom manager for the Activity model.

    This manager provides methods to retrieve activities based on their
    specific types, facilitating easier queries for different activity
    categories.
    """

    def get_queryset(self):
        """
        Get the custom queryset for the Activity model.

        Returns
        -------
        ActivityQuerySet
            The custom queryset for activities.
        """
        return ActivityQuerySet(self.model, using=self._db)

    def skill_trainings(self):
        """
        Retrieve all skill training activities.

        Returns
        -------
        QuerySet
            A queryset of skill training activities.
        """
        return self.get_queryset().filter_by_activity_type("skill_training")

    def movement_trainings(self):
        """
        Retrieve all movement training activities.

        Returns
        -------
        QuerySet
            A queryset of movement training activities.
        """
        return self.get_queryset().filter_by_activity_type("movement_training")

    def community_services(self):
        """
        Retrieve all community service activities.

        Returns
        -------
        QuerySet
            A queryset of community service activities.
        """
        return self.get_queryset().filter_by_activity_type("community_service")

    def prayer_movements(self):
        """
        Retrieve all prayer movement activities.

        Returns
        -------
        QuerySet
            A queryset of prayer movement activities.
        """
        return self.get_queryset().filter_by_activity_type("prayer_movement")


class Activity(TimestampedModel, models.Model):
    """
    Model representing an activity in the application.
    """

    title = models.CharField(max_length=150)
    description = tinymce_models.HTMLField()
    summary = models.TextField(
        validators=[
            MinLengthValidator(
                135, message="Summary must be at least 135 characters long"
            ),
            MaxLengthValidator(
                200, message="Summary must be no more than 200 characters long"
            ),
        ],
    )

    slug = models.SlugField(
        unique=True,
        editable=False,
    )
    event = models.ForeignKey(
        Event,
        related_name="activities",
        on_delete=models.CASCADE,
    )
    activity_type = models.CharField(
        max_length=50,
        choices=ACTIVITY_TYPE_CHOICES,
    )
    meeting_link = models.URLField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    default_facilitation_invitation_message = models.TextField(
        null=True,
        blank=True,
    )
    tags = TaggableManager(blank=True)
    author = models.ForeignKey(
        Profile,
        related_name="activities_organized",
        on_delete=models.CASCADE,
    )
    requirements = tinymce_models.HTMLField(
        null=True,
        blank=True,
    )

    SCOPE_CHOICES = [
        ("comprehensive", "Comprehensive"),
        ("abridged", "Abridged"),
    ]
    scope = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES,
        default="comprehensive",
    )
    beneficiary = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    objects = ActivityManager()

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ["start_date"]

    def save(self, *args, **kwargs):
        """
        Override the save method to generate a slug if not present and validate date fields.

        Parameters
        ----------
        *args : positional arguments
            Arguments passed to the parent save method.
        **kwargs : keyword arguments
            Keyword arguments passed to the parent save method.

        Raises
        ------
        ValidationError
            If the end date is earlier than the start date.

        Notes
        -----
        If the slug field is empty, it generates a slug from the title using `slugify`.
        It also checks that the start date is not later than the end date before saving.
        """
        # Generate slug from title if it's empty
        if not self.slug:
            self.slug = slugify(self.title)
        # Ensure end_date is not earlier than start_date
        if self.end_date and self.start_date > self.end_date:  # pragma: no cover
            raise ValidationError("End date cannot be earlier than start date.")
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return the string representation of the activity, typically its title.

        Returns
        -------
        str
            The string representation of the activity instance.
        """
        return self.title

    # def get_absolute_url(self):
    #     """
    #     Get the absolute URL for the activity detail page.

    #     Returns
    #     -------
    #     str
    #         The absolute URL for the activity detail.
    #     """
    #     return reverse(
    #         "activities:activity_detail",
    #         kwargs={
    #             "activity_slug": self.slug,
    #         },
    #     )

    def get_share_url(self, request):  # pragma: no cover
        """
        Build the absolute URL for sharing the activity.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.

        Returns
        -------
        str
            The absolute share URL for the activity.
        """
        return request.build_absolute_uri(self.get_absolute_url())

    def registration_is_open(self):
        """
        Check if registration for the activity is open.

        Returns
        -------
        bool
            True if registration is open, False otherwise.
        """
        today = date.today()

        # Registration should be closed if today is the event start date or
        # later, or the activity start date or later
        if today >= self.start_date or today >= self.event.start_date:
            return False

        # If no registration deadline is set, registration is open
        if self.event.registration_deadline_date is None:
            return True

        # Registration is open if today is before the registration deadline
        return today < self.event.registration_deadline_date

    def is_upcoming(self):
        """
        Check if the activity is upcoming.

        Returns
        -------
        bool
            True if the activity is scheduled in the future, False otherwise.
        """
        return self.start_date >= date.today()

    def is_ongoing(self):
        """
        Check if the activity is ongoing.

        Returns
        -------
        bool
            True if the activity is currently taking place, False otherwise.
        """
        today = date.today()
        return self.start_date <= today <= self.end_date

    def is_past(self):
        """
        Check if the activity has already occurred.

        Returns
        -------
        bool
            True if the activity is in the past, False otherwise.
        """
        return self.end_date < date.today()

    @property
    def default_image(self):  # pragma: no cover
        """
        Get the default image URL for the activity based on its type.

        Returns
        -------
        str
            The URL of the default image for the activity type.
        """

        return ACTIVITY_DEFAULT_IMAGES.get(self.activity_type)


class ActivityRegistration(
    TimestampedModel,
    models.Model,
):
    """
    Model representing a registration for an activity.

    This model tracks both profile-based registrations and guest-based registrations
    for activities. It also manages tokens for confirmation and rejection of registrations.
    """

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Cancelled", "Cancelled"),
        ("Confirmed", "Confirmed"),
        ("Registered", "Registered"),
    ]

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="registrations",
    )

    profile = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="activity_registrations",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Registered",
    )

    guest_name = models.CharField(
        null=True,
        blank=True,
        max_length=150,
    )

    guest_email = models.EmailField(
        null=True,
        blank=True,
        max_length=150,
    )

    is_guest = models.BooleanField(default=False)

    confirmation_token = models.UUIDField(
        unique=True,
        default=uuid4,
        null=True,
        blank=True,
        editable=False,
    )
    rejection_token = models.UUIDField(
        unique=True,
        default=uuid4,
        null=True,
        blank=True,
        editable=False,
    )

    @classmethod
    def profile_registrations(cls):
        """
        Retrieve all registrations that are linked to profiles (non-guest registrations).

        Returns
        -------
        QuerySet
            A queryset of registrations where `is_guest` is False.
        """
        return cls.objects.filter(is_guest=False)

    @property
    def registration_name(self):
        """
        Get the name of the registrant, either the profile's name or guest name.

        Returns
        -------
        str
            The name of the registrant. If it's a profile-based registration,
            returns the profile name, otherwise returns the guest name.
        """
        if self.profile:
            return self.profile.get_full_name()

        return self.guest_name

    def __str__(self):
        """
        Return a string representation of the registration.

        Returns
        -------
        str
            A string in the format of 'registrant name - activity title'.
        """
        if self.profile:
            return f"{self.registration_name} - {self.activity.title}"

        return f"{self.registration_name} - {self.activity.title}"

    class Meta:
        """
        Meta options for the ActivityRegistration model.

        - Orders registrations first by activity, then by guest name.
        """

        ordering = [
            "activity",
            "guest_name",
        ]


class ActivityAttendance(models.Model):
    """
    Model representing attendance for a specific activity registration.

    This model records the check-in time for a registration and is linked to an
    `ActivityRegistration` instance. It handles both profile-based and
    guest-based attendance.
    """

    registration = models.OneToOneField(
        ActivityRegistration,
        related_name="attendance",
        on_delete=models.CASCADE,
    )

    """
    A one-to-one relationship with `ActivityRegistration`.

    This links the attendance record to a specific registration.
    """

    check_in_time = models.DateTimeField(
        null=True,
        blank=True,
    )
    """
    The time when the registrant checked in to the activity.

    This field is optional and can be null or blank if check-in hasn't
    occurred yet.
    """

    def __str__(self):
        """
        Return a string representation of the attendance record.

        Returns
        -------
        str
            A string indicating the attendance for a specific user or guest at an activity.
        """
        if self.registration.profile:
            return (
                f"Attendance for {self.registration.profile.user.username} at "
                f"{self.registration.activity.title}"
            )

        return (
            f"Attendance for {self.registration.guest_name} at "
            f"{self.registration.activity.title}"
        )


class ActivityFacilitator(models.Model):
    """
    Model representing a facilitator for a specific activity.

    This model links an activity to a facilitator (a profile) who is responsible for
    conducting or leading the activity.
    """

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Rejected", "Rejected"),
        ("Confirmed", "Confirmed"),
    ]

    activity = models.ForeignKey(
        Activity,
        related_name="facilitators",
        on_delete=models.CASCADE,
    )
    """
    A foreign key relationship to the `Activity` model.

    This field links the facilitator to the specific activity they are facilitating.
    """

    facilitator = models.ForeignKey(
        Profile,
        related_name="facilitated_activities",
        on_delete=models.CASCADE,
    )
    """
    A foreign key relationship to the `Profile` model.

    This field represents the facilitator, linking to the profile of the
    individual facilitating the activity.
    """

    def __str__(self):
        """
        Return a string representation of the activity facilitator.

        Returns
        -------
        str
            A string indicating the facilitator's name and the activity
            they are facilitating.
        """
        return f"{self.facilitator.get_full_name()} for {self.activity.title}"


class ActivityFacilitatorInvitation(TimestampedModel, models.Model):
    """
    Model representing an invitation for a facilitator to lead an activity.

    This model stores information about invitations sent to facilitators
    to participate in an activity, including the invitation status and
    related tokens.
    """

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]
    """Choices for the invitation status, indicating whether it is
    pending, accepted, or rejected."""

    activity = models.ForeignKey(
        Activity,
        related_name="facilitator_invitations",
        on_delete=models.CASCADE,
    )
    """
    A foreign key relationship to the `Activity` model.

    This field links the invitation to the specific activity the facilitator
    is being invited to lead.
    """

    facilitator = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="facilitator_invitations",
    )
    """
    A foreign key relationship to the `Profile` model.

    This field links the invitation to the facilitator (profile) who is being invited.
    """

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
    )
    """A field indicating the current status of the invitation."""

    invitation_message = models.TextField(
        null=True,
        blank=True,
    )
    """Optional message sent along with the invitation."""

    confirmation_token = models.UUIDField(unique=True, default=uuid4, editable=False)
    """A unique token used to confirm the invitation."""

    rejection_token = models.UUIDField(unique=True, default=uuid4, editable=False)
    """A unique token used to reject the invitation."""

    def __str__(self):
        """
        Return a string representation of the facilitator invitation.

        Returns
        -------
        str
            A string indicating the facilitator's name and the activity
            they are invited to facilitate.
        """
        return (
            f"Invitation for {self.facilitator.get_full_name()} to "
            f"facilitate {self.activity.title}"
        )

    class Meta:
        """Ensure that each facilitator can only be invited once to an activity."""

        unique_together = ("activity", "facilitator")


class ActivityFeedback(models.Model):
    """
    Model representing feedback given by a participant for an activity.
    """

    activity = models.ForeignKey(
        Activity,
        related_name="feedbacks",
        on_delete=models.CASCADE,
    )
    """
    Foreign key to the Activity being reviewed.
    """

    profile = models.ForeignKey(
        Profile,
        related_name="activity_feedbacks",
        on_delete=models.CASCADE,
    )
    """
    Foreign key to the Profile giving the feedback. Now uses 'activity_feedbacks' to avoid clashes.
    """

    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )
    """
    Rating for the activity between 1 and 5.
    """

    comment = models.TextField(blank=True)
    """Optional comment about the activity."""

    def __str__(self):
        """
        Return a string representation of the feedback.

        Returns
        -------
        str
            A string in the format 'Feedback for {activity title} by {profile name}'.
        """

        return f"Feedback for {self.activity.title} by {self.profile.get_full_name()}"


class ActivityImage(models.Model):  # pragma: no cover
    """
    Model representing images associated with an activity.
    """

    activity = models.ForeignKey(
        Activity,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = CloudinaryField(
        validators=[validate_image],
        null=True,
        blank=True,
        folder="kns/images/activities/",
    )
    caption = models.TextField(
        null=True,
        blank=True,
    )
    primary = models.BooleanField(default=False)

    def __str__(self):
        """
        Return a string representation of the activity image.

        Returns
        -------
        str
            The activity title and the image caption.
        """
        return f"{self.activity.title} - {self.caption}"

    def save(self, *args, **kwargs):
        """
        Override the save method to ensure only one image is set as primary for each activity.
        If no primary image is set, select the first image.

        Parameters
        ----------
        *args : positional arguments
            Additional positional arguments to pass to the parent save method.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to the parent save method.

        Raises
        ------
        Exception
            Any exceptions raised by the parent save method.

        Notes
        -----
        If the current image is marked as primary, all other images for the same activity
        will have their primary flag unset. After saving, if no primary image is set for
        the activity, the first image associated with the activity will be set as primary.
        """
        if self.primary:
            # Unset the primary flag for other images of this activity
            ActivityImage.objects.filter(
                activity=self.activity,
                primary=True,
            ).update(primary=False)

        super().save(*args, **kwargs)

        # If no primary image is set for this activity, set the first one as primary
        if not ActivityImage.objects.filter(
            activity=self.activity,
            primary=True,
        ).exists():
            first_image = ActivityImage.objects.filter(
                activity=self.activity,
            ).first()
            if first_image:
                first_image.primary = True
                first_image.save()
