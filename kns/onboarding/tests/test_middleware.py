from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.groups.models import GroupMember
from kns.groups.tests.factories import GroupFactory
from kns.onboarding.middleware import OnboardingMiddleware
from kns.onboarding.models import ProfileOnboarding
from kns.profiles.models import Profile


class OnboardingMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = OnboardingMiddleware(
            lambda request: HttpResponse(""),
        )

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass",
        )

        self.client.login(
            email="testuser@example.com",
            password="testpass",
        )

        self.profile = self.user.profile
        self.profile_onboarding = ProfileOnboarding.objects.create(
            profile=self.profile,
            current_step=1,
        )

        self.profile.role = "leader"
        self.profile.save()

        self.group = GroupFactory(
            name="Bible Study Group",
            location_country="Nigeria",
            location_city="Lagos",
            leader=self.profile,
        )

        self.group_member = GroupMember.objects.create(
            group=self.group,
            profile=self.profile,
        )

    def test_redirect_to_onboarding_step(self):
        # Set the profile onboarding to a non-complete state
        self.profile_onboarding.current_step = 1
        self.profile_onboarding.save()

        # Make a request to a view that should trigger the onboarding redirect
        response = self.client.get(reverse("profiles:index"))

        # Assert that the response is a redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse(
                "onboarding:index",
            ),
        )

    def test_no_redirection_when_onboarded(self):
        # Test that no redirection occurs when user is onboarded
        self.profile.is_onboarded = True
        self.profile.save()

        response = self.client.get(reverse("profiles:index"))

        self.assertEqual(response.status_code, 200)

    def test_no_redirection_for_admin_logout_onboarding_routes(self):
        # Test that no redirection occurs for admin, logout, or onboarding routes
        self.profile.is_onboarded = False
        self.profile.save()

        # Test admin route
        response = self.client.get(
            reverse(
                "profiles:index",
            ),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        # Test logout route
        response = self.client.get(
            reverse(
                "accounts:logout",
            ),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        # Test onboarding route
        response = self.client.get(
            reverse(
                "profiles:index",
            ),
        )

        self.assertEqual(
            response.status_code,
            302,
        )
