from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from kns.custom_user.models import User
from kns.onboarding.context_processors import onboarding_data
from kns.onboarding.models import ProfileOnboarding


class TestContextProcessors(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass",
        )

        self.profile = self.user.profile
        self.profile.role = "leader"
        self.profile.save()

    def test_onboarding_data_user_not_authenticated(self):
        """
        Test that no onboarding data is returned if the user is not authenticated.
        """
        request = self.factory.get("/onboarding/")
        request.user = MagicMock(is_authenticated=False)

        context = onboarding_data(request)

        self.assertEqual(context, {})

    def test_onboarding_data_path_not_onboarding(self):
        """
        Test that no onboarding data is returned if the path does not
        include 'onboarding'.
        """
        request = self.factory.get("/some-other-path/")
        request.user = self.user

        context = onboarding_data(request)

        self.assertEqual(context, {})

    def test_onboarding_data_profile_onboarding_exists(self):
        """
        Test that the existing ProfileOnboarding instance is used and data is returned.
        """
        ProfileOnboarding.objects.create(profile=self.profile)

        request = self.factory.get("/onboarding/")
        request.user = self.user

        with patch(
            "kns.onboarding.models.ProfileOnboarding.get_onboarding_steps_list",
            return_value=[
                {"name": "Step 1"},
                {"name": "Step 2"},
            ],
        ):
            with patch(
                "kns.onboarding.models.ProfileOnboarding.get_current_step",
                return_value={"name": "Step 1"},
            ):
                context = onboarding_data(request)

        self.assertEqual(
            len(context["onboarding_steps_list"]),
            2,
        )
        self.assertEqual(
            context["onboarding_steps_list"][0]["name"],
            "Step 1",
        )
        self.assertEqual(
            context["onboarding_data"]["name"],
            "Step 1",
        )
