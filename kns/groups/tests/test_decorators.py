"""
Tests for decorators in the `groups` app.
"""

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.test import RequestFactory, TestCase

from kns.custom_user.models import User
from kns.groups.decorators import group_leader_required
from kns.groups.models import Group


# Define the dummy_view outside the test class
@group_leader_required
def dummy_view(request, group, *args, **kwargs):
    """
    A dummy view to test the group_leader_required decorator.

    Parameters
    ----------
    request : HttpRequest
        The incoming request object.
    group : Group
        The group instance resolved by the decorator.
    *args : tuple
        Additional positional arguments.
    **kwargs : dict
        Additional keyword arguments.

    Returns
    -------
    HttpResponse
        A simple HTTP response indicating success.
    """
    return HttpResponse("Success!")


class TestGroupLeaderRequiredDecorator(TestCase):
    """
    Test suite for the `group_leader_required` decorator.
    """

    def setUp(self):
        """
        Set up test users and groups.
        """
        self.factory = RequestFactory()

        # Create users
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )
        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password123",
        )

        # Create profiles (assuming a OneToOneField from User to Profile)
        self.profile = self.user.profile
        self.profile.is_onboarded = True
        self.profile.save()

        self.other_profile = self.other_user.profile
        self.other_profile.is_onboarded = True
        self.other_profile.save()

        # Create a group with the first user as the leader
        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            description="A description for the test group.",
        )

    def test_group_leader_required_success(self):
        """
        Test that the view allows access when the user is the group leader.
        """
        # Create a mock GET request
        request = self.factory.get("/dummy-view/test-group/")
        request.user = self.user  # The leader

        # Call the dummy_view directly with the group_slug
        response = dummy_view(request, self.group.slug)

        # Check if the response is as expected
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Success!")

    def test_group_leader_required_not_leader(self):
        """
        Test that the view raises PermissionDenied if the user is not the group leader.
        """
        # Create a mock GET request
        request = self.factory.get("/dummy-view/test-group/")
        request.user = self.other_user  # Not the leader

        # Attempt to call the dummy_view and expect PermissionDenied
        with self.assertRaises(PermissionDenied) as context:
            dummy_view(request, self.group.slug)

        # Optionally, check the exception message
        self.assertEqual(
            str(context.exception),
            "You are not the leader of this group.",
        )

    def test_group_leader_required_group_not_found(self):
        """
        Test that the view raises Http404 if the group does not exist.
        """

        # Create a mock GET request
        request = self.factory.get("/dummy-view/non-existent-group/")
        request.user = self.user  # Attempting with a leader

        # Attempt to call the dummy_view and expect Http404
        with self.assertRaises(Http404) as context:
            dummy_view(
                request,
                "non-existent-group",
            )

        # Optionally, check the exception message
        self.assertIn(
            "No Group matches the given query.",
            str(context.exception),
        )
