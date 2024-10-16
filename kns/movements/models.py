"""
Models for the `movements` app.
"""

from uuid import uuid4

from django.db import models
from tinymce import models as tinymce_models

from kns.core.modelmixins import TimestampedModel
from kns.profiles.models import Profile


class Movement(
    TimestampedModel,
    models.Model,
):
    """
    Model representing a Movement, which can be a regular or a prayer movement.

    Attributes
    ----------
    title : str
        The title of the movement.
    slug : UUID
        A unique identifier generated for the movement.
    prayer_movement : bool
        Indicates if the movement is a prayer movement.
    content : HTMLField
        The main content of the movement, stored as HTML.
    author : Profile
        The profile that created the movement.
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

    prayer_movement = models.BooleanField(default=False)

    content = tinymce_models.HTMLField()

    author = models.ForeignKey(
        Profile,
        related_name="movements_created",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of a Movement instance.

        Returns
        -------
        str
            The title of the movement.
        """
        return self.title

    class Meta:
        unique_together = ("title", "slug")


class MovementTopic(
    TimestampedModel,
    models.Model,
):
    """
    Model representing a topic related to movements.

    Attributes
    ----------
    title : str
        The title of the movement topic.
    slug : UUID
        A unique identifier generated for the topic.
    content : HTMLField
        The main content of the movement topic, stored as HTML.
    author : Profile
        The profile that created the movement topic.
    """

    title = models.CharField(
        unique=True,
        max_length=150,
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
        related_name="movement_topics",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return a string representation of a MovementTopic instance.

        Returns
        -------
        str
            The title of the movement topic.
        """
        return self.title

    class Meta:
        unique_together = (
            "title",
            "slug",
        )


class MovementSyllabusItem(models.Model):
    """
    Model representing an item (topic) in a Movement's syllabus.

    Attributes
    ----------
    movement : ForeignKey
        The movement to which the topic is assigned.
    topic : ForeignKey
        The topic being assigned to the movement.
    created_at : DateTimeField
        The date and time when the assignment was created.
    """

    movement = models.ForeignKey(
        "Movement",
        related_name="syllabus_items",
        on_delete=models.CASCADE,
    )

    topic = models.ForeignKey(
        "MovementTopic",
        related_name="syllabus_assignments",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        """
        Return a string representation of the MovementSyllabusItem instance.

        Returns
        -------
        str
            A string indicating the movement and topic relationship.
        """
        return f"{self.topic.title} in {self.movement.title}'s syllabus"

    class Meta:
        unique_together = ("movement", "topic")


class ProfileMovement(models.Model):
    """
    Model representing the relationship between a profile and a movement.

    Attributes
    ----------
    profile : ForeignKey
        A reference to the profile associated with the movement.
    movement : ForeignKey
        A reference to the movement associated with the profile.
    created_at : DateTimeField
        The date and time when the profile joined the movement.
    updated_at : DateTimeField
        The date and time when the record was last updated.
    """

    profile = models.ForeignKey(
        Profile,
        related_name="movements",
        on_delete=models.CASCADE,
    )

    movement = models.ForeignKey(
        Movement,
        related_name="profiles",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    COMPREHENSION_LEVELS = [
        (1, "Beginner"),
        (2, "Intermediate"),
        (3, "Expert"),
    ]

    comprehension = models.IntegerField(
        choices=COMPREHENSION_LEVELS,
        default=1,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
    )

    class Meta:
        unique_together = ["profile", "movement"]

    def __str__(self) -> str:
        """
        Return a string representation of a ProfileMovement instance.

        Returns
        -------
        str
            The full name of the profile associated with the movement.
        """
        return f"{self.profile.get_full_name()}"

    def increment_comprehension(self):
        """
        Increment the comprehension level of the profile associated with the movement.

        This method increases the comprehension level by one, up to a maximum level of 3 (Expert).
        It saves the updated comprehension level to the database.
        """
        if self.comprehension < 3:  # Assuming 3 is the max level
            self.comprehension += 1
            self.save()
