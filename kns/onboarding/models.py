"""
Models for the `onboarding` app.

This module defines the `ProfileOnboarding` model, which manages the onboarding
process for user profiles. The onboarding steps vary based on the profile's
role and visitor status, and steps can be navigated through the `next` and
`back` methods.
"""

from django.core.cache import cache
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils import timezone

from kns.core.modelmixins import TimestampedModel
from kns.onboarding.constants import ONBOARDING_STEPS
from kns.profiles.models import Profile


class ProfileOnboarding(models.Model):
    """
    Model representing the onboarding process for a user profile.

    This model tracks the current step in the onboarding process and provides
    methods to navigate through the steps. The steps available depend on the
    profile's role (e.g., leader or regular member) and whether the user is
    a visitor.
    """

    profile = models.OneToOneField(
        Profile,
        related_name="onboarding",
        on_delete=models.CASCADE,
    )
    current_step = models.IntegerField(default=1)

    def back(self):
        """
        Move back to the previous onboarding step, ensuring it doesn't go
        below step 1.

        If the current step is already the first step, it remains unchanged.
        """

        if self.current_step > 1:
            self.current_step = self.current_step - 1
            self.save()

    def next(self, profile):
        """
        Move to the next onboarding step, ensuring it doesn't exceed the
        number of available steps for the given profile.

        Parameters
        ----------
        profile : Profile
            The profile for which the onboarding process is being performed.
        """
        max_steps = len(self.get_onboarding_steps_list(profile))

        self.current_step = min(self.current_step + 1, max_steps)

        self.save()

    def get_onboarding_steps_list(self, profile):
        """
        Return the list of onboarding steps based on the profile's role and
        visitor status. The steps are cached for performance optimization.

        Parameters
        ----------
        profile : Profile
            The profile for which to retrieve the onboarding steps.

        Returns
        -------
        list
            A list of dictionaries containing the details of each onboarding step.
        """
        cache_key = f"onboarding_steps_{profile.id}"
        steps = cache.get(cache_key)

        if not steps:
            # Start with the default steps
            steps = [
                ONBOARDING_STEPS["profile"],
                ONBOARDING_STEPS["agree"],
            ]

            # Include additional steps based on the profile's role
            if not getattr(profile, "is_visitor", False):
                if ONBOARDING_STEPS["involvement"] not in steps:
                    steps.insert(
                        1,
                        ONBOARDING_STEPS["involvement"],
                    )

                if (
                    getattr(
                        profile,
                        "role",
                        "member",
                    )
                    == "leader"
                    and ONBOARDING_STEPS["group"] not in steps
                ):
                    steps.insert(2, ONBOARDING_STEPS["group"])

            # Set cache
            cache.set(cache_key, steps, timeout=3600)

        return steps

    def get_current_step(self, profile):
        """
        Retrieve the current onboarding step for the profile.

        Parameters
        ----------
        profile : Profile
            The profile for which to retrieve the current step.

        Returns
        -------
        dict
            A dictionary representing the current onboarding step, including
            details such as the title, description, and template name.
        """
        onboarding_steps_list = self.get_onboarding_steps_list(profile)

        if self.is_last_step(profile):
            return onboarding_steps_list[len(onboarding_steps_list) - 1]

        return onboarding_steps_list[self.current_step - 1]

    def is_last_step(self, profile):
        """
        Determine whether the current step is the last step in the onboarding
        process for the profile.

        Parameters
        ----------
        profile : Profile
            The profile for which to check if the current step is the last.

        Returns
        -------
        bool
            True if the current step is the last, False otherwise.
        """
        onboarding_steps_list = self.get_onboarding_steps_list(profile)

        return self.current_step > len(onboarding_steps_list)


class ProfileCompletionTask(TimestampedModel, models.Model):
    """
    Represent a task that a profile needs to complete for profile integration.

    Attributes
    ----------
    profile : ForeignKey
        The profile who owns the task.
    task_name : CharField
        The name of the task.
    task_description : CharField
        The description of the task.
    is_complete : BooleanField
        Whether the task has been completed.
    created_at : DateTimeField
        The date and time the task was created.
    completed_at : DateTimeField
        The date and time the task was completed (optional).
    """

    TASKS = [
        (
            "complete_profile",
            "Complete your profile",
        ),
        (
            "register_group",
            "Register group",
        ),
        (
            "register_first_member",
            "Register first member",
        ),
        (
            "add_vocations_skills",
            "Add vocations, skills, and interests",
        ),
        (
            "browse_events",
            "Browse events near you",
        ),
    ]

    class Meta:
        unique_together = (
            "profile",
            "task_name",
        )

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="completion_tasks",
    )
    task_name = models.CharField(
        max_length=100,
        choices=TASKS,
    )
    task_description = models.CharField(
        max_length=150,
        validators=[
            MinLengthValidator(120),
            MaxLengthValidator(150),
        ],
    )
    description = models.TextField()
    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def mark_complete(self):
        """
        Mark the task as complete and sets the completion time.
        """
        self.is_complete = True
        self.completed_at = timezone.now()
        self.save()

    def __str__(self):
        """
        Return a string representation of the task.

        Returns
        -------
        str
            A string in the format of "{task_name} for {profile_full_name}".
        """
        return f"{self.task_name} for {self.profile.get_full_name()}"


class ProfileCompletion(models.Model):
    """
    Track the overall completion of a profile.

    Attributes
    ----------
    profile : OneToOneField
        The profile whose completion is tracked.
    """

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="profile_completion",
    )

    @property
    def is_profile_complete(self):
        """
        Return whether the profile is fully complete by checking all tasks.

        Returns
        -------
        bool
            True if all tasks are complete, False otherwise.
        """
        return not self.profile.completion_tasks.filter(
            is_complete=False,
        ).exists()

    def remaining_tasks(self):
        """
        Return a QuerySet of incomplete tasks.

        Returns
        -------
        QuerySet
            A QuerySet containing incomplete tasks for the profile.
        """
        return self.profile.completion_tasks.filter(is_complete=False)

    def completed_tasks(self):
        """
        Return a QuerySet of completed tasks.

        Returns
        -------
        QuerySet
            A QuerySet containing completed tasks for the profile.
        """
        return self.profile.completion_tasks.filter(is_complete=True)

    def total_tasks(self):
        """
        Return the total number of tasks assigned to the profile.

        Returns
        -------
        int
            The total count of tasks for the profile.
        """
        return self.profile.completion_tasks.count()

    def completed_task_count(self):
        """
        Return the number of completed tasks.

        Returns
        -------
        int
            The count of completed tasks for the profile.
        """
        return self.completed_tasks().count()

    def completion_percentage(self):
        """
        Return the percentage of tasks completed as an integer.
        If there are no tasks, return 100 (consider profile complete).

        Returns
        -------
        int
            The percentage of completed tasks, or 100 if there are no tasks.
        """
        total = self.total_tasks()

        if total == 0:
            return 100

        return int((self.completed_task_count() / total) * 100)

    def __str__(self):
        """
        Return a string representation of the ProfileCompletion instance.

        Returns
        -------
        str
            A string in the format of "Profile completion for {profile_full_name}".
        """
        return f"Profile completion for {self.profile.get_full_name()}"
