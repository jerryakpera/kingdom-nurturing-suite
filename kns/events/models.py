"""
Models for the `events` app.
"""

from cloudinary.models import CloudinaryField
from django.core.validators import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from taggit.managers import TaggableManager
from tinymce import models as tinymce_models

from kns.core.modelmixins import ModelWithLocation, ModelWithStatus, TimestampedModel
from kns.profiles.models import Profile

from . import constants as event_constants
from .utils import get_min_max_validator, validate_image


class Event(
    TimestampedModel,
    ModelWithLocation,
    ModelWithStatus,
    models.Model,
):
    """
    Model representing an event in the application.
    """

    title = models.CharField(
        max_length=event_constants.EVENT_TITLE_MAX_LENGTH,
        validators=get_min_max_validator(
            event_constants.EVENT_TITLE_MIN_LENGTH,
            event_constants.EVENT_TITLE_MAX_LENGTH,
            (
                "Event title must be at least "
                f"{event_constants.EVENT_TITLE_MIN_LENGTH} characters"
            ),
            (
                "Event title must be no more than "
                f"{event_constants.EVENT_TITLE_MAX_LENGTH} characters"
            ),
        ),
    )
    summary = models.TextField(
        default="",
        validators=get_min_max_validator(
            event_constants.EVENT_SUMMARY_MIN_LENGTH,
            event_constants.EVENT_SUMMARY_MAX_LENGTH,
            f"Summary must be at least {event_constants.EVENT_SUMMARY_MIN_LENGTH} characters",
            f"Summary must be no more than {event_constants.EVENT_SUMMARY_MAX_LENGTH} characters",
        ),
    )
    cancel_reason = models.TextField(
        null=True,
        blank=True,
        default="",
        validators=get_min_max_validator(
            event_constants.EVENT_CANCEL_REASON_MIN_LENGTH,
            event_constants.EVENT_CANCEL_REASON_MAX_LENGTH,
            (
                "Reason for cancelling must be at least "
                f"{event_constants.EVENT_CANCEL_REASON_MIN_LENGTH} characters"
            ),
            (
                "Reason for cancelling must be no more than "
                f"{event_constants.EVENT_CANCEL_REASON_MAX_LENGTH} characters"
            ),
        ),
    )
    description = tinymce_models.HTMLField()
    slug = models.SlugField(unique=True, editable=False)
    tags = TaggableManager(blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    registration_deadline_date = models.DateField(
        null=True,
        blank=True,
    )

    refreshments = models.BooleanField(default=False)
    accommodation = models.BooleanField(default=False)

    event_contact_name = models.CharField(max_length=50)
    event_contact_email = models.EmailField(blank=True)

    archived_at = models.DateField(null=True, blank=True)

    author = models.ForeignKey(
        Profile,
        related_name="events_organized",
        on_delete=models.CASCADE,
    )

    class Meta:
        indexes = [
            models.Index(fields=["start_date"]),
            models.Index(fields=["end_date"]),
            models.Index(fields=["slug"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F("start_date")),
                name="end_date_after_start_date",
            ),
        ]

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

    @property
    def duration(self):
        """
        Calculate the duration of the event.

        Returns
        -------
        int
            Number of days between the start and end dates.
        """
        if self.end_date and self.start_date:
            return (self.end_date - self.start_date).days

        return 0

    def __str__(self):
        """
        Return the string representation of the event, typically its title.

        Returns
        -------
        str
            The string representation of the event instance.
        """
        return self.title

    def location_display(self):
        """
        Display the location of the event as a formatted string.

        Returns
        -------
        str
            The location of the event formatted as "Country, City" or
            "Country" if no city is provided, or "None" if no location
            is provided.
        """
        location_str = "None"
        if self.location_country:
            location_str = self.location_country.name
            if self.location_city:
                location_str += f", {self.location_city}"

        return location_str

    def days_until_event(self):
        """
        Calculate the number of days remaining until the event starts.

        Returns
        -------
        int
            The number of days until the event starts or 0 if the event has already started.
        """
        today = timezone.now().date()
        days_left = (self.start_date - today).days

        return max(days_left, 0)

    def has_registration_deadline_passed(self):
        """
        Check if the registration deadline has passed.

        Returns
        -------
        bool
            True if the deadline has passed, False otherwise.
        """
        today = timezone.now().date()

        return today > self.registration_deadline_date

    def is_upcoming(self):
        """
        Check if the event is upcoming.

        Returns
        -------
        bool
            True if the event has not yet started, False otherwise.
        """
        today = timezone.now().date()
        return self.start_date and today < self.start_date

    def get_primary_image(self):  # pragma: no cover
        """
        Return the primary image for this event. If no primary image has been set,
        return the first image added for the event.

        Returns
        -------
        EventImage
            The primary image if one exists, otherwise the first image
            added or None if no images exist.
        """
        # Try to get the primary image
        primary_image = self.galleries.filter(
            primary=True,
        ).first()

        if primary_image:
            return primary_image

        # If no primary image, return the first image added to the event
        return self.galleries.first()


class EventImage(models.Model):  # pragma: no cover
    """
    Model representing images associated with an event.
    """

    event = models.ForeignKey(
        Event,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = CloudinaryField(
        validators=[validate_image],
        null=True,
        blank=True,
        folder="kns/images/events/",
    )
    caption = models.TextField(
        null=True,
        blank=True,
    )
    primary = models.BooleanField(default=False)

    def __str__(self):
        """
        Return a string representation of the event image.

        Returns
        -------
        str
            The event title and the image caption.
        """
        return f"{self.event.title} - {self.caption}"

    def save(self, *args, **kwargs):
        """
        Override the save method to ensure only one image is set as primary for each event.
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
        If the current image is marked as primary, all other images for the same event
        will have their primary flag unset. After saving, if no primary image is set for
        the event, the first image associated with the event will be set as primary.
        """
        if self.primary:
            # Unset the primary flag for other images of this event
            EventImage.objects.filter(event=self.event, primary=True).update(
                primary=False
            )

        super().save(*args, **kwargs)

        # If no primary image is set for this event, set the first one as primary
        if not EventImage.objects.filter(
            event=self.event,
            primary=True,
        ).exists():
            first_image = EventImage.objects.filter(
                event=self.event,
            ).first()
            if first_image:
                first_image.primary = True
                first_image.save()
