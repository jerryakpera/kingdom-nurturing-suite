from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.groups.forms import GroupForm
from kns.groups.models import Group

from . import test_constants


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
            description=test_constants.VALID_GROUP_DESCRIPTION,
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

    def test_group_overview_view(self):
        """
        Test the group_overview view for authenticated users to ensure
        it renders the specific group.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:group_overview",
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
            "groups/pages/group_overview.html",
        )

        # Ensure the group overview are present
        self.assertIn(
            "Test Group",
            response.content.decode(),
        )

    def test_group_overview_view_not_found(self):
        """
        Test the group_overview view with a non-existent group slug.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:group_overview",
            kwargs={
                "group_slug": "non-existent-group",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)

    def test_group_members_view(self):
        """
        Test the group_members view for authenticated users to
        ensure it renders the specific group.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:group_members",
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
            "groups/pages/group_members.html",
        )

        # Ensure the group members are present
        self.assertIn(
            "Test Group",
            response.content.decode(),
        )

    def test_group_members_view_not_found(self):
        """
        Test the group_members view with a non-existent group slug.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:group_members",
            kwargs={
                "group_slug": "non-existent-group",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)

    def test_group_activities_view(self):
        """
        Test the group_activities view for authenticated users to
        ensure it renders the specific group.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:group_activities",
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
            "groups/pages/group_activities.html",
        )

        # Ensure the group activities are present
        self.assertIn(
            "Test Group",
            response.content.decode(),
        )

    def test_group_activities_view_not_found(self):
        """
        Test the group_activities view with a non-existent group slug.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:group_activities",
            kwargs={
                "group_slug": "non-existent-group",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)

    def test_group_subgroups_view(self):
        """
        Test the group_subgroups view for authenticated users to
        ensure it renders the specific group.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:group_subgroups",
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
            "groups/pages/group_subgroups.html",
        )

        # Ensure the group subgroups are present
        self.assertIn(
            "Test Group",
            response.content.decode(),
        )

    def test_group_subgroups_view_not_found(self):
        """
        Test the group_subgroups view with a non-existent group slug.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:group_subgroups",
            kwargs={
                "group_slug": "non-existent-group",
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(response.status_code, 404)


class TestRegisterGroupView(TestCase):
    def setUp(self):
        self.client = Client()

        # Set up a user and profile for testing
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )
        self.profile = self.user.profile

        # Log the user in
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )

        # URL for the register group view
        self.register_group_url = reverse("groups:register_group")

    def test_register_group_get_response(self):
        """
        A logged-in user gets a valid response and sees the
        group registration form.
        """
        response = self.client.get(self.register_group_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "groups/pages/register_group.html",
        )
        self.assertIsInstance(
            response.context["group_form"],
            GroupForm,
        )

    def test_register_group_post_valid_data(self):
        """
        A logged-in user can create a group with valid data.
        """
        data = {
            "name": "Test Group",
            "description": test_constants.VALID_GROUP_DESCRIPTION,
            "location_city": "Lagos",
            "location_country": "NG",
        }

        response = self.client.post(
            self.register_group_url,
            data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), 1)

        group = Group.objects.first()

        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.leader, self.profile)

        url = reverse(
            "groups:group_overview",
            kwargs={
                "group_slug": group.slug,
            },
        )

        self.assertEqual(
            response.url,
            url,
        )

    def test_register_group_post_valid_data_parent_group(self):
        """
        A logged-in group member can create a group with valid data.
        """
        data = {
            "name": "Test Group",
            "description": test_constants.VALID_GROUP_DESCRIPTION,
            "location_city": "Lagos",
            "location_country": "NG",
        }

        origin_user = User.objects.create_user(
            email="origin@user.com",
            password="password",
        )
        origin_group = Group.objects.create(
            leader=origin_user.profile,
            name="Origin group",
            slug="origin-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        origin_group.add_member(self.profile)

        response = self.client.post(
            self.register_group_url,
            data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), 2)

        group = Group.objects.last()

        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.leader, self.profile)

        url = reverse(
            "groups:group_overview",
            kwargs={
                "group_slug": group.slug,
            },
        )

        self.assertEqual(
            response.url,
            url,
        )

    def test_register_group_post_invalid_data(self):
        """
        A logged-in user cannot create a group with invalid data.
        """
        data = {
            "name": "",
            "description": test_constants.VALID_GROUP_DESCRIPTION,
            "location_city": "Lagos",
            "location_country": "NG",
        }

        response = self.client.post(
            self.register_group_url,
            data,
        )

        # Check response status and template used
        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "groups/pages/register_group.html",
        )

        # Access the form from the response context
        form = response.context.get("group_form")

        # Ensure form is not None and is an instance of GroupForm
        self.assertIsNotNone(form)
        self.assertIsInstance(form, GroupForm)

        # Check if the form has errors
        self.assertTrue(form.errors)

    def test_register_group_user_already_leading_group(self):
        """
        A logged-in user who is already leading a group receives
        a warning message and is redirected to the group's detail page.
        """
        # Set up a group led by the profile
        self.group = Group.objects.create(
            leader=self.profile,
            name="Existing Group",
            slug="existing-group",
            description="An existing group description",
        )

        # Add the profile as a leader
        self.profile.group_led = self.group
        self.profile.save()

        # Attempt to access the group registration view
        response = self.client.get(self.register_group_url)

        # Check the redirection to the existing group's detail page
        self.assertRedirects(response, self.group.get_absolute_url())


class TestEditGroupView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user and their profile
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password123",
        )

        # Create a group led by the user
        self.group = Group.objects.create(
            leader=self.user.profile,
            name="Test Group",
            slug="test-group",
            location_city="Lagos",
            location_country="NG",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        # Create another group led by the other user
        self.other_group = Group.objects.create(
            leader=self.other_user.profile,
            name="Other Group",
            slug="other-group",
            location_city="Lagos",
            location_country="NG",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

    def test_edit_group_view_authenticated(self):
        """
        Test the edit_group view for an authenticated user who is the group leader.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:edit_group",
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
            "groups/pages/edit_group.html",
        )

        # Ensure the form is present
        self.assertIsInstance(
            response.context["group_form"],
            GroupForm,
        )

    def test_edit_group_view_non_leader(self):
        """
        Test that a user who is not the leader of the group cannot edit the group.
        """
        self.client.login(
            email="otheruser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:edit_group",
            kwargs={"group_slug": self.group.slug},
        )
        response = self.client.get(url)

        # Check if the response redirects to the group's overview page
        self.assertRedirects(
            response,
            reverse(
                "groups:group_overview",
                kwargs={
                    "group_slug": self.group.slug,
                },
            ),
        )

        # Ensure a warning message is displayed
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You do not have permission to edit this group.",
        )

    def test_edit_group_view_unauthenticated(self):
        """
        Test that an unauthenticated user is redirected to the login page.
        """
        url = reverse(
            "groups:edit_group",
            kwargs={"group_slug": self.group.slug},
        )
        response = self.client.get(url)

        # Check if the response redirects to the login page
        self.assertRedirects(
            response,
            f"/accounts/login/?next={url}",
        )

    def test_edit_group_post_success(self):
        """
        Test successfully editing a group by the group leader.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )

        url = reverse(
            "groups:edit_group",
            kwargs={
                "group_slug": self.group.slug,
            },
        )

        data = {
            "slug": self.group.slug,
            "name": "Updated Group Name",
            "location_city": "Lagos",
            "location_country": "NG",
            "description": test_constants.VALID_GROUP_DESCRIPTION,
        }

        response = self.client.post(url, data)

        # Refresh the group from the database to check for updates
        self.group.refresh_from_db()

        # Assert the group's name and description have been updated
        self.assertEqual(
            self.group.name,
            "Updated Group Name",
        )

        # Check if the response redirects to the group's overview page
        self.assertRedirects(
            response,
            reverse(
                "groups:group_overview",
                kwargs={
                    "group_slug": self.group.slug,
                },
            ),
        )

        # Ensure a success message is displayed
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Group updated successfully!",
        )

    def test_edit_group_post_invalid(self):
        """
        Test submitting invalid data when editing a group.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        url = reverse(
            "groups:edit_group",
            kwargs={"group_slug": self.group.slug},
        )
        data = {
            "name": "",  # Invalid data: empty name
            "description": "An updated description for the group.",
            "slug": self.group.slug,
        }
        response = self.client.post(url, data)

        # Check if the response status code is 200 OK (re-renders the form)
        self.assertEqual(response.status_code, 200)

        # Check if the form is present with errors
        self.assertIsInstance(
            response.context["group_form"],
            GroupForm,
        )
        self.assertTrue(response.context["group_form"].errors)
