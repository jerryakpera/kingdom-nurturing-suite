import pytest
from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User

from ..models import Profile


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )
        User.objects.create_user(email="adminuser@example.com", password="oldpassword")

        self.client.login(
            email="testuser@example.com",
            password="oldpassword",
        )

        self.profile = self.user.profile

        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

    def test_index_view(self):
        """
        Test the index view to ensure it renders correctly and lists profiles.
        """
        response = self.client.get(reverse("profiles:index"))

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, "profiles/pages/index.html")

        self.assertIn("profiles", response.context)
        self.assertEqual(
            response.context["profiles"].count(),
            1,
        )

        # Ensure the profile is listed
        assert b"Test User" in response.content

    def test_profile_detail_view(self):
        """
        Test the profile_detail view to ensure it renders the specific profile.
        """
        url = reverse(
            "profiles:profile_detail",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, "profiles/pages/profile-detail.html")

        # Ensure the profile details are present
        self.assertIn("Test User", response.content.decode())

    def test_profile_detail_view_not_found(self):
        """
        Test the profile_detail view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:profile_detail", kwargs={"profile_slug": "non-existent"}
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)
