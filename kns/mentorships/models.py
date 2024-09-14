"""
Models for the `mentorships` app.
"""

from uuid import uuid4

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from tinymce import models as tinymce_models

from kns.core.constants import MENTORSHIP_GOAL_TYPES, MENTORSHIP_STATUS_CHOICES
from kns.core.modelmixins import ModelWithStatus, TimestampedModel
from kns.profiles.models import Profile


class MentorshipArea(
    TimestampedModel,
    ModelWithStatus,
    models.Model,
):
    """
    A model representing an area of mentorship.

    The `MentorshipArea` model stores information about a specific area in which
    mentorship is offered. It includes fields for the title, slug, content,
    and the author (profile) who created the mentorship area. The model also
    inherits timestamp fields for tracking creation and modification times,
    and a status field for indicating the current state of the mentorship area.

    Methods
    -------
    __str__():
        Return the title of the mentorship area, providing a string
        representation of the object.
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
        related_name="mentorship_areas_created",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of the MentorshipArea instance.

        This method returns the title of the mentorship area, which is used
        to represent the object in a readable form, such as in Django admin
        or when the object is printed.

        Returns
        -------
        str
            The title of the mentorship area.
        """

        return self.title


class MentorshipGoal(
    TimestampedModel,
    ModelWithStatus,
    models.Model,
):
    """
    A model representing a mentorship goal.

    The `MentorshipGoal` model stores information about specific goals for
    mentorship. It includes fields for the title, slug, content, the author
    (profile) who created the goal, and the type of the goal. The model also
    inherits timestamp fields for tracking creation and modification times,
    and a status field for indicating the current state of the mentorship goal.

    Methods
    -------
    __str__():
        Return the title of the mentorship goal, providing a string
        representation of the object.
    """

    title = models.CharField(max_length=150, unique=True)
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
        related_name="mentorship_goalss_created",
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        max_length=30,
        choices=MENTORSHIP_GOAL_TYPES,
        default="primary",
    )

    def __str__(self) -> str:
        """
        Return a string representation of the MentorshipGoal instance.

        This method returns the title of the mentorship goal, which is used
        to represent the object in a readable form, such as in Django admin
        or when the object is printed.

        Returns
        -------
        str
            The title of the mentorship goal.
        """

        return self.title


class MentorshipAreaMentorshipGoal(
    TimestampedModel,
    models.Model,
):
    """
    A model representing the relationship between mentorship areas and mentorship goals.

    The `MentorshipAreaMentorshipGoal` model links a specific mentorship area to a specific
    mentorship goal. It includes foreign key relationships to both `MentorshipArea` and
    `MentorshipGoal` models. This model facilitates the association between areas and goals,
    ensuring that each combination of area and goal is unique.

    Methods
    -------
    __str__():
        Return a string representation of the MentorshipAreaMentorshipGoal instance, which
        includes the titles of both the mentorship area and the mentorship goal.
    """

    mentorship_area = models.ForeignKey(
        MentorshipArea, related_name="goals", on_delete=models.CASCADE
    )
    mentorship_goal = models.ForeignKey(
        MentorshipGoal, related_name="areas", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        """
        Return a string representation of the MentorshipAreaMentorshipGoal instance.

        This method returns a formatted string that includes the titles of both the mentorship
        area and the mentorship goal associated with this relationship.

        Returns
        -------
        str
            A string combining the titles of the mentorship area and the mentorship goal,
            formatted as "MentorshipAreaTitle (MentorshipGoalTitle)".
        """
        return f"{self.mentorship_area.title} ({self.mentorship_goal.title})"

    class Meta:
        unique_together = (
            "mentorship_area",
            "mentorship_goal",
        )


class ProfileMentorshipArea(models.Model):
    """
    A model representing the relationship between a user profile and a mentorship area.

    The `ProfileMentorshipArea` model links a specific user profile to a specific
    mentorship area. It includes foreign key relationships to both `Profile` and
    `MentorshipArea` models, indicating which profiles are associated with which
    mentorship areas. This model also tracks the creation and last modification
    times of the relationships.

    Methods
    -------
    __str__():
        Return a string representation of the ProfileMentorshipArea instance, which
        includes the name of the profile and the title of the mentorship area.
    """

    profile = models.ForeignKey(
        Profile, related_name="mentorship_areas", on_delete=models.CASCADE
    )
    mentorship_area = models.ForeignKey(
        MentorshipArea, related_name="profiles", on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self) -> str:
        """
        Return a string representation of the ProfileMentorshipArea instance.

        This method returns a formatted string that includes the name of the profile and
        the title of the mentorship area associated with this relationship.

        Returns
        -------
        str
            A string combining the name of the profile and the title of the mentorship area,
            formatted as "ProfileName MentorshipAreaTitle".
        """
        return f"{self.profile.get_full_name()} {self.mentorship_area.title}"

    class Meta:
        unique_together = ("profile", "mentorship_area")


class Mentorship(TimestampedModel, ModelWithStatus, models.Model):
    """
    A model representing a mentorship relationship between a mentor and a mentee.

    The `Mentorship` model tracks the details of a mentorship relationship, including
    the associated mentorship area, mentor, mentee, and key dates. It also includes fields
    for tracking the duration of the mentorship, approval requirements, and cancellation
    details. The model inherits timestamp fields for creation and modification times, and
    a status field for tracking the current state of the mentorship.

    Methods
    -------
    __str__():
        Return a string representation of the Mentorship instance, which includes the names
        of the mentor and mentee.
    """

    slug = models.SlugField(
        unique=True,
        default=uuid4,
        null=True,
        blank=True,
        editable=False,
    )
    mentorship_area = models.ForeignKey(
        MentorshipArea,
        related_name="mentorships",
        on_delete=models.CASCADE,
    )
    mentor = models.ForeignKey(
        Profile,
        related_name="mentorships_as_mentor",
        on_delete=models.CASCADE,
    )
    mentee = models.ForeignKey(
        Profile,
        related_name="mentorships_as_mentee",
        on_delete=models.CASCADE,
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )
    expected_end_date = models.DateField(
        null=True,
        blank=True,
    )
    end_date = models.DateField(
        null=True,
        blank=True,
    )
    cancel_date = models.DateField(
        null=True,
        blank=True,
    )
    cancel_reason = models.TextField(
        null=True,
        blank=True,
    )
    duration = models.IntegerField(default=0)
    mentor_approval_required = models.BooleanField(
        default=True,
    )
    group_leader_approval_required = models.BooleanField(
        default=False,
    )

    author = models.ForeignKey(
        Profile,
        related_name="mentorships_created",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=20,
        choices=MENTORSHIP_STATUS_CHOICES,
        default="draft",
    )

    def __str__(self) -> str:
        """
        Return a string representation of the Mentorship instance.

        This method returns a formatted string that includes the names of the mentor and the mentee
        involved in the mentorship relationship.

        Returns
        -------
        str
            A string formatted as "MentorName -> MenteeName".
        """
        return f"{self.mentor.get_full_name()} -> {self.mentee.get_full_name()}"


class MentorshipMentorshipGoal(TimestampedModel, models.Model):
    """
    A model representing the relationship between a mentorship and a mentorship goal.

    The `MentorshipMentorshipGoal` model links a specific mentorship to a specific
    mentorship goal. It includes foreign key relationships to both the `Mentorship`
    and `MentorshipGoal` models. This model also tracks when the goal was completed.

    Methods
    -------
    __str__():
        Return a string representation of the MentorshipMentorshipGoal instance, which includes
        the title of the mentorship goal and the names of the mentor and mentee involved.
    """

    mentorship = models.ForeignKey(
        Mentorship,
        related_name="goals",
        on_delete=models.CASCADE,
    )
    mentorship_goal = models.ForeignKey(
        MentorshipGoal,
        related_name="mentorships",
        on_delete=models.CASCADE,
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        """
        Return a string representation of the MentorshipMentorshipGoal instance.

        This method returns a formatted string that includes the title of the mentorship goal,
        and the names of the mentor and mentee associated with the mentorship.

        Returns
        -------
        str
            A string formatted as "MentorshipGoalTitle - MentorName mentoring MenteeName".
        """
        return (
            f"{self.mentorship_goal.title} - {self.mentorship.mentor.get_full_name()} "
            f"mentoring {self.mentorship.mentee.get_full_name()}"
        )

    class Meta:
        unique_together = (
            "mentorship",
            "mentorship_goal",
        )


class MentorEndorsement(TimestampedModel, models.Model):
    """
    A model representing an endorsement given to a mentor by another profile.

    The `MentorEndorsement` model links an endorser profile to a mentor profile, indicating that
    the endorser has endorsed the mentor. It includes foreign key relationships to both `Profile`
    models for the mentor and endorser. The model also allows for an optional
    message from the endorser.

    Methods
    -------
    __str__():
        Return a string representation of the MentorEndorsement instance, which includes
        the names of the endorser and the mentor.
    """

    class Meta:
        unique_together = (
            "mentor",
            "endorser",
        )

    mentor = models.ForeignKey(
        Profile,
        related_name="endorsements",
        on_delete=models.CASCADE,
    )
    endorser = models.ForeignKey(
        Profile,
        related_name="given_endorsements",
        on_delete=models.CASCADE,
    )
    message = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        """
        Return a string representation of the MentorEndorsement instance.

        This method returns a formatted string that includes the name of the endorser and
        the name of the mentor being endorsed.

        Returns
        -------
        str
            A string formatted as "EndorserName endorsed MentorName".
        """
        return f"{self.endorser.get_full_name()} endorsed {self.mentor.get_full_name()}"


class MentorshipFeedback(TimestampedModel, models.Model):
    """
    A model representing feedback given on a specific mentorship.

    The `MentorshipFeedback` model links feedback to a particular mentorship and
    includes details about the author of the feedback, the comments provided, and
    a rating given. This model helps track and manage feedback related to mentorships.

    Methods
    -------
    __str__():
        Return a string representation of the MentorshipFeedback instance, which includes
        a description of the mentorship being reviewed.
    """

    mentorship = models.ForeignKey(
        Mentorship,
        related_name="feedback",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        Profile,
        related_name="feedbacks",
        on_delete=models.CASCADE,
    )
    comments = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self) -> str:
        """
        Return a string representation of the MentorshipFeedback instance.

        This method returns a formatted string that includes a description of the
        mentorship for which the feedback was provided.

        Returns
        -------
        str
            A string formatted as "Feedback for MentorshipInstance".
        """
        return f"Feedback for {self.mentorship}"
