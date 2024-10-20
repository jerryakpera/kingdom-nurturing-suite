from django.contrib.auth.models import AnonymousUser
from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.events.permissions import (
    event_creation_permission_required,
    has_event_creation_permission,
)
from kns.groups.models import Group
from kns.groups.tests import test_constants as group_test_constants


class TestHasEventCreationPermission(TestCase):
    def setUp(self):
        # Create a verified user who is a leader of a group
        self.user = User.objects.create_user(
            email="verified_user@example.com",
            password="password",
        )
        self.user.verified = True
        self.user.save()

        self.profile = self.user.profile

        # Create a group with the verified user as the leader
        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            location_country="NG",
            location_city="Bauchi",
            description=group_test_constants.VALID_GROUP_DESCRIPTION,
        )

        # Create an unverified user
        self.user_unverified = User.objects.create_user(
            email="unverified_user@example.com",
            password="password",
        )
        self.user_unverified.verified = False
        self.user_unverified.save()

        # Create a normal user who is verified but not a group leader
        self.user_without_leadership = User.objects.create_user(
            email="normal_user@example.com",
            password="password",
        )
        self.user_without_leadership.verified = True
        self.user_without_leadership.save()

        # Create an anonymous user
        self.anonymous_user = AnonymousUser()

    def test_verified_user_with_group_leadership(self):
        """
        Test if a verified user who is a leader of a group has permission
        to create an event.
        """
        result = has_event_creation_permission(self.user)
        self.assertTrue(result)

    def test_verified_user_without_group_leadership(self):
        """
        Test if a verified user who is not a leader of any group does not
        have permission to create an event.
        """
        result = has_event_creation_permission(self.user_without_leadership)
        self.assertFalse(result)

    def test_unverified_user(self):
        """
        Test if an unverified user does not have permission to create an event.
        """
        result = has_event_creation_permission(self.user_unverified)
        self.assertFalse(result)

    def test_anonymous_user(self):
        """
        Test if an anonymous user does not have permission to create an event.
        """

        result = has_event_creation_permission(self.anonymous_user)

        self.assertFalse(result)


class TestEventCreationPermissionRequired(TestCase):
    def setUp(self):
        self.client = Client()  # Use Django's test client

        # Create a verified user who is a leader of a group
        self.user_verified = User.objects.create_user(
            email="verified_user@example.com",
            password="password",
        )
        self.user_verified.verified = True
        self.user_verified.save()

        self.leader_profile = self.user_verified.profile

        self.user_verified.verified = True
        self.user_verified.agreedToTerms = True
        self.user_verified.save()

        self.leader_profile.is_onboarded = True
        self.leader_profile.save()

        # Create a group with the verified user as the leader
        self.leader_group = Group.objects.create(
            leader=self.leader_profile,
            name="Leader Group",
            slug="leader-group",
            location_country="NG",
            location_city="Bauchi",
            description="A group led by a verified user.",
        )

        # Create an unverified user
        self.user_unverified = User.objects.create_user(
            email="unverified_user@example.com",
            password="password",
        )
        self.user_unverified.verified = False
        self.user_unverified.save()

        self.unverified_profile = self.user_unverified.profile

        self.unverified_profile.is_onboarded = True
        self.unverified_profile.save()

    def test_redirects_anonymous_user(self):
        """
        Test that an anonymous user is redirected when trying to access
        a view that requires event creation permission.
        """
        response = self.client.get(
            reverse("events:create_event")
        )  # Using the test client
        self.assertRedirects(response, reverse("events:index"))

    def test_redirects_unverified_user(self):
        """
        Test that an unverified user is redirected when trying to access
        a view that requires event creation permission.
        """

        self.client.login(
            email="unverified_user@example.com",
            password="password",
        )

        response = self.client.get(reverse("events:create_event"))

        self.assertRedirects(response, reverse("events:index"))

    def test_allows_verified_leader_user(self):
        """
        Test that a verified user who is a group leader can access a view
        that requires event creation permission.
        """

        self.client.login(
            email="verified_user@example.com",
            password="password",
        )

        response = self.client.get(reverse("events:create_event"))

        # Check if the response is successful (HTTP 200 OK)
        self.assertEqual(response.status_code, 200)


# Dummy view to test permission
def dummy_view(request):
    return "Success"
