import pytest
from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.groups.models import Group


class TestGroupViews(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )

        # Create a group
        self.group = Group.objects.create(
            leader=self.user.profile,
            name="Test Group",
            slug="test-group",
            description="A test group description",
        )

    def test_index_view_authenticated(self):
        """
        Test the index view for authenticated users to ensure
        it renders correctly and lists groups.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        response = self.client.get(reverse("groups:index"))

        # Check if the response status code is 200 OK
        self.assertEqual(
            response.status_code,
            200,
        )

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "groups/pages/index.html",
        )

        self.assertIn(
            "groups",
            response.context,
        )
        self.assertEqual(
            response.context["groups"].count(),
            1,
        )

        # Ensure the profile is listed
        assert b"Test Group" in response.content

    def test_group_detail_view(self):
        """
        Test the group_detail view for authenticated users to ensure it renders the specific group.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:group_detail",
            kwargs={
                "group_slug": self.group.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "groups/pages/group_detail.html",
        )

        # Ensure the group details are present
        self.assertIn(
            "Test Group",
            response.content.decode(),
        )

    def test_group_detail_view_not_found(self):
        """
        Test the group_detail view with a non-existent group slug.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:group_detail",
            kwargs={
                "group_slug": "non-existent-group",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)
