from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.groups.models import Group
from kns.groups.tests import test_constants as group_test_consants
from kns.profiles.models import Profile


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="oldpassword",
        )
        User.objects.create_user(
            email="adminuser@example.com",
            password="oldpassword",
        )

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
        self.assertTemplateUsed(response, "profiles/pages/profile_detail.html")

        # Ensure the profile details are present
        self.assertIn("Test User", response.content.decode())

    def test_profile_detail_view_not_found(self):
        """
        Test the profile_detail view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:profile_detail",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)

    def test_profile_involvements_view(self):
        """
        Test the profile_involvements view to ensure it renders the specific profile.
        """
        url = reverse(
            "profiles:profile_involvements",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "profiles/pages/profile_involvements.html",
        )

        # Ensure the profile involvementss are present
        self.assertIn(
            "Test User",
            response.content.decode(),
        )

    def test_profile_involvements_view_not_found(self):
        """
        Test the profile_involvements view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:profile_involvements",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(
            response.status_code,
            404,
        )

    def test_profile_trainings_view(self):
        """
        Test the profile_trainings view to ensure it renders the specific profile.
        """
        url = reverse(
            "profiles:profile_trainings",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "profiles/pages/profile_trainings.html",
        )

        # Ensure the profile trainingss are present
        self.assertIn(
            "Test User",
            response.content.decode(),
        )

    def test_profile_trainings_view_not_found(self):
        """
        Test the profile_trainings view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:profile_trainings",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(
            response.status_code,
            404,
        )

    def test_profile_activities_view(self):
        """
        Test the profile_activities view to ensure it renders the specific profile.
        """
        url = reverse(
            "profiles:profile_activities",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "profiles/pages/profile_activities.html",
        )

        # Ensure the profile activitiess are present
        self.assertIn(
            "Test User",
            response.content.decode(),
        )

    def test_profile_activities_view_not_found(self):
        """
        Test the profile_activities view with a non-existent profile slug.
        """
        url = reverse(
            "profiles:profile_activities",
            kwargs={
                "profile_slug": "non-existent",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(
            response.status_code,
            404,
        )

    def test_profile_settings_view(self):
        """
        Test the profile_settings view to ensure it renders and
        updates the profile settings.
        """

        # Get the profile settings page
        response = self.client.get(self.profile.get_settings_url())

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "profiles/pages/profile_settings.html",
        )

        # Ensure the form is present in the response
        self.assertIn("profile_settings_form", response.context)

        # Now test the POST request to update the profile settings
        new_data = {
            "bio_details_is_visible": False,
            "contact_details_is_visible": False,
            # Add other profile fields here if necessary
        }

        response = self.client.post(
            self.profile.get_settings_url(),
            data=new_data,
        )

        # Refresh the profile from the database
        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.bio_details_is_visible,
            False,
        )
        self.assertEqual(
            self.profile.contact_details_is_visible,
            False,
        )

        # Check if the response redirects after saving
        self.assertEqual(response.status_code, 302)

        # Ensure the success message is in the messages
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"{self.profile.get_full_name()} settings updated",
        )


class MakeLeaderViewTests(TestCase):
    def setUp(self):
        """
        Set up the test users, profiles, and groups.
        """
        self.leader_user = User.objects.create_user(
            email="leader@example.com",
            password="password123",
        )
        self.member_user = User.objects.create_user(
            email="member@example.com",
            password="password123",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
        )

        self.leader_profile = self.leader_user.profile
        self.member_profile = self.member_user.profile
        self.other_profile = self.other_user.profile

        self.member_profile.first_name = "John"
        self.member_profile.last_name = "Doe"
        self.member_profile.gender = "Male"
        self.member_profile.date_of_birth = "1990-01-01"
        self.member_profile.place_of_birth_country = "USA"
        self.member_profile.place_of_birth_city = "New York"
        self.member_profile.location_country = "USA"
        self.member_profile.location_city = "New York"
        self.member_profile.slug = "john-doe"
        self.member_profile.save()

        self.member_user.verified = True
        self.member_user.agreed_to_terms = True
        self.member_user.save()

        # Create a group
        self.group = Group.objects.create(
            name="Test Group",
            slug="test-group",
            leader=self.leader_profile,
            description=group_test_consants.VALID_GROUP_DESCRIPTION,
        )
        self.group.add_member(self.member_profile)

        self.url = reverse(
            "profiles:make_leader",
            args=[self.member_profile.slug],
        )

    def test_make_leader_success(self):
        """
        Test that a leader can successfully promote a group member to a leader.
        """
        self.client.login(
            email="leader@example.com",
            password="password123",
        )

        response = self.client.get(self.url)

        self.member_profile.refresh_from_db()
        self.assertEqual(self.member_profile.role, "leader")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "John Doe has been successfully promoted to a leader.",
        )

        self.assertRedirects(response, self.member_profile.get_absolute_url())

    def test_make_leader_not_leading_group(self):
        """
        Test that a user who is not leading the group cannot promote someone to leader.
        """
        self.client.login(
            email="other@example.com",
            password="password123",
        )

        response = self.client.post(self.url)

        self.member_profile.refresh_from_db()
        self.assertEqual(
            self.member_profile.role,
            "member",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "You are not authorized to perform this action.",
        )

        self.assertRedirects(response, self.member_profile.get_absolute_url())

    def test_make_leader_not_group_member(self):
        """
        Test that a leader cannot promote someone who is not a member
        of their group.
        """
        self.client.login(email="leader@example.com", password="password123")

        other_profile_url = reverse(
            "profiles:make_leader", args=[self.other_profile.slug]
        )
        response = self.client.post(other_profile_url)

        self.other_profile.refresh_from_db()
        self.assertEqual(self.other_profile.role, "member")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            f"You must be the leader of "
            f"{self.other_profile.get_full_name()} to perform this action.",
        )

        self.assertRedirects(response, self.other_profile.get_absolute_url())

    def test_make_leader_ineligible_profile(self):
        """
        Test that an ineligible profile cannot be promoted to leader.
        """
        self.client.login(
            email="leader@example.com",
            password="password123",
        )

        with patch.object(
            Profile,
            "can_become_leader_role",
            return_value=False,
        ):
            response = self.client.post(self.url)

        self.member_profile.refresh_from_db()
        self.assertEqual(
            self.member_profile.role,
            "member",
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            f"{self.member_profile.get_full_name()} is not eligible to become a leader.",
        )

        self.assertRedirects(
            response,
            self.member_profile.get_absolute_url(),
        )
