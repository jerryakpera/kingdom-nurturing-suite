from django.conf import settings
from django.core.cache import cache
from django.test import TestCase

from kns.custom_user.models import User
from kns.onboarding.models import ProfileOnboarding


class TestProfileOnboardingModel(TestCase):
    def setUp(self):
        """
        Setup method to create a User and Profile instance linked to it.
        Also initializes onboarding steps in settings for the tests.
        """
        self.user = User.objects.create_user(
            email="test.user@example.com",
            password="password123",
        )
        self.profile = self.user.profile
        self.profile.role = "leader"
        self.profile.save()

        self.onboarding = ProfileOnboarding.objects.create(
            profile=self.profile,
            current_step=1,
        )

        # Mock onboarding steps in settings
        settings.ONBOARDING_STEPS = {
            "profile": {
                "name": "Profile details",
                "template_name": "onboarding/profile.html",
            },
            "involvement": {
                "name": "Involvement preferences",
                "template_name": "onboarding/involvement.html",
            },
            "group": {
                "name": "Group registration",
                "template_name": "onboarding/group.html",
            },
            "agree": {
                "name": "Terms and Conditions",
                "template_name": "onboarding/agree.html",
            },
        }

    def tearDown(self):
        """
        Clear cache after each test.
        """
        cache.clear()

    def test_back_method(self):
        """
        Test that the `back` method correctly decreases the current step,
        ensuring it doesn't go below step 1.
        """
        self.onboarding.current_step = 2
        self.onboarding.save()

        self.onboarding.back()
        self.assertEqual(self.onboarding.current_step, 1)

        self.onboarding.back()  # Step should not go below 1
        self.assertEqual(self.onboarding.current_step, 1)

    def test_next_method(self):
        """
        Test that the `next` method correctly increases the current step,
        ensuring it doesn't exceed the number of available steps.
        """
        self.onboarding.next(self.profile)
        self.assertEqual(self.onboarding.current_step, 2)

        # There are 4 steps for a leader
        self.onboarding.current_step = 4
        self.onboarding.save()

        # Should not go beyond step 4
        self.onboarding.next(self.profile)
        self.assertEqual(self.onboarding.current_step, 4)

    def test_get_onboarding_steps_list(self):
        """
        Test that the `get_onboarding_steps_list` returns the correct list
        of steps based on the profile's role.
        """

        steps = self.onboarding.get_onboarding_steps_list(self.profile)

        # Leader should have 4 steps
        self.assertEqual(len(steps), 4)
        self.assertEqual(steps[0]["name"], "Profile details")
        self.assertEqual(
            steps[3]["name"],
            "Terms and Conditions",
        )

        # Change role to regular member and check step list
        self.profile.role = "member"
        self.profile.save()

        # Clear cache to ensure we get the correct steps for the new role
        cache.delete(f"onboarding_steps_{self.profile.id}")

        steps = self.onboarding.get_onboarding_steps_list(self.profile)

        self.assertEqual(len(steps), 3)  # Regular member should have 3 steps

    def test_get_current_step(self):
        """
        Test that `get_current_step` returns the correct current step
        based on the profile's onboarding progress.
        """
        current_step = self.onboarding.get_current_step(self.profile)

        self.assertEqual(
            current_step["name"],
            "Profile details",
        )

        self.onboarding.current_step = 2
        self.onboarding.save()

        current_step = self.onboarding.get_current_step(self.profile)

        self.assertEqual(
            current_step["name"],
            "Involvement preferences",
        )

    def test_is_last_step(self):
        """
        Test that `is_last_step` correctly identifies if the current step is the last step.
        """
        self.onboarding.current_step = 5
        self.onboarding.save()

        self.assertTrue(self.onboarding.is_last_step(self.profile))

        self.onboarding.current_step = 3
        self.onboarding.save()

        self.assertFalse(self.onboarding.is_last_step(self.profile))
