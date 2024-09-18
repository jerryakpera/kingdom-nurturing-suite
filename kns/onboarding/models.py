"""
Models for the `onboarding` app.

This module defines the `ProfileOnboarding` model, which manages the onboarding
process for user profiles. The onboarding steps vary based on the profile's
role and visitor status, and steps can be navigated through the `next` and
`back` methods.
"""

from django.core.cache import cache
from django.db import models

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
        self.current_step = max(1, self.current_step - 1)
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
