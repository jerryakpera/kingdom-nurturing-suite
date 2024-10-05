from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.faith_milestones.models import FaithMilestone, GroupFaithMilestone
from kns.groups.forms import GroupForm
from kns.groups.models import Group
from kns.mentorships.models import MentorshipArea, ProfileMentorshipArea
from kns.skills.models import ProfileInterest, ProfileSkill, Skill
from kns.vocations.models import ProfileVocation, Vocation

from . import test_constants


class TestGroupViews(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )

        self.profile = self.user.profile
        self.profile.is_onboarded = True
        self.profile.save()

        # Create a group
        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            location_country="NG",
            location_city="Bauchi",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

    def test_index_view_authenticated(self):
        """
        Test the index view for authenticated users to ensure
        it renders correctly and includes profile completion and groups.
        """
        user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="password",
        )
        profile2 = user2.profile

        self.group.add_member(profile=profile2)

        # Create a group
        self.group2 = Group.objects.create(
            leader=profile2,
            name="Test Group 2",
            location_country="NG",
            location_city="Bauchi",
            parent=self.group,
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        # Log in the test user
        self.client.login(
            email=self.user.email,
            password="password123",
        )

        response = self.client.get(reverse("core:index"))

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "core/pages/index.html",
        )

        # Check that 'profile_completion' is in the context
        self.assertIn("profile_completion", response.context)

        # If there is a group led by the user, 'local_groups' should be in the context
        self.assertIn("local_groups", response.context)
        self.assertEqual(
            response.context["local_groups"].count(),
            1,
        )

        # Ensure the correct group is listed in 'local_groups'
        self.assertIn(self.group2, response.context["local_groups"])

        # Ensure the group's name appears in the page description
        self.assertIn("Test Group 2", response.content.decode())

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

        self.profile.is_onboarded = True
        self.profile.save()

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

        self.client.login(
            email="testuser@example.com",
            password="password123",
        )

        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.role = "leader"
        self.profile.gender = "male"
        self.profile.date_of_birth = "1997-08-08"
        self.profile.location_country = "NG"
        self.profile.location_city = "NG"

        self.user.verified = True
        self.user.agreed_to_terms = True

        self.user.save()
        self.profile.save()

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

        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.role = "leader"
        self.profile.gender = "male"
        self.profile.date_of_birth = "1997-08-08"
        self.profile.location_country = "NG"
        self.profile.location_city = "NG"

        self.user.verified = True
        self.user.agreed_to_terms = True

        self.user.save()
        self.profile.save()

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
            location_country="NG",
            location_city="Bauchi",
            slug="origin-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.role = "leader"
        self.profile.gender = "male"
        self.profile.date_of_birth = "1997-08-08"
        self.profile.location_country = "NG"
        self.profile.location_city = "NG"

        self.user.verified = True
        self.user.agreed_to_terms = True

        self.user.save()
        self.profile.save()

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

        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.role = "leader"
        self.profile.gender = "male"
        self.profile.date_of_birth = "1997-08-08"
        self.profile.location_country = "NG"
        self.profile.location_city = "NG"

        self.user.verified = True
        self.user.agreed_to_terms = True

        self.user.save()
        self.profile.save()

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
            location_country="NG",
            location_city="Bauchi",
            description="An existing group description",
        )

        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.role = "leader"
        self.profile.gender = "male"
        self.profile.date_of_birth = "1997-08-08"
        self.profile.location_country = "NG"
        self.profile.location_city = "NG"
        self.profile.group_led = self.group

        self.user.verified = True
        self.user.agreed_to_terms = True

        self.user.save()
        self.profile.save()

        # Attempt to access the group registration view
        response = self.client.get(self.register_group_url)

        # Check the redirection to the existing group's detail page
        self.assertRedirects(response, reverse("groups:index"))


class TestEditGroupView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user and their profile
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )

        self.profile = self.user.profile
        self.profile.is_onboarded = True

        self.profile.save()

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password123",
        )

        self.other_profile = self.other_user.profile
        self.other_profile.is_onboarded = True
        self.other_profile.save()

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


class TestEditGroupMilestonesView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user and a group
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )

        self.profile = self.user.profile

        self.profile.is_onboarded = True
        self.profile.save()

        self.group = Group.objects.create(
            leader=self.user.profile,
            name="Test Group",
            slug="test-group",
            location_country="NG",
            location_city="Bauchi",
            description="A test group description",
        )

        self.faith_milestone1 = FaithMilestone.objects.create(
            title="Faith milestone 1",
            description="This is test description for a faith milestone",
            type="group",
            author=self.profile,
        )
        self.faith_milestone2 = FaithMilestone.objects.create(
            type="group",
            title="Faith milestone 2",
            description="This is test description for a faith milestone",
            author=self.profile,
        )
        self.faith_milestone3 = FaithMilestone.objects.create(
            type="group",
            title="Faith milestone 3",
            description="This is test description for a faith milestone",
            author=self.profile,
        )
        self.faith_milestone4 = FaithMilestone.objects.create(
            type="group",
            title="Faith milestone 4",
            description="This is test description for a faith milestone",
            author=self.profile,
        )

        self.url = reverse(
            "groups:edit_group_milestones",
            kwargs={
                "group_slug": self.group.slug,
            },
        )

    def test_edit_group_milestones_get(self):
        """
        Test that the edit_group_milestones view renders correctly for a GET request.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "groups/pages/edit_group_faith_milestones.html",
        )
        self.assertIn(
            "group_milestones_form",
            response.context,
        )

    def test_edit_group_milestones_post_valid_data(self):
        """
        Test that valid data updates the group milestones and redirects correctly.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )

        data = {
            "faith_milestones": [
                self.faith_milestone1.pk,
                self.faith_milestone2.pk,
            ],
        }

        response = self.client.post(
            self.url,
            data,
        )

        # Check if the response status code is 302 (redirect)
        self.assertEqual(
            response.status_code,
            302,
        )

        # Verify that the milestones have been added to the group
        milestones = GroupFaithMilestone.objects.filter(
            group=self.group,
        )

        self.assertEqual(
            milestones.count(),
            2,
        )

        self.assertTrue(
            milestones.filter(
                faith_milestone=self.faith_milestone1,
            ).exists(),
        )
        self.assertTrue(
            milestones.filter(
                faith_milestone=self.faith_milestone2,
            ).exists(),
        )

    def test_edit_group_milestones_post_duplicate_milestones(self):
        """
        Test that posting duplicate milestones does not create multiple entries.
        """
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )

        GroupFaithMilestone.objects.create(
            group=self.group,
            faith_milestone=self.faith_milestone1,
        )

        data = {
            "faith_milestones": [
                self.faith_milestone1.pk,
                self.faith_milestone2.pk,
            ],
        }
        response = self.client.post(self.url, data)

        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Verify that no duplicate milestones are created
        milestones = GroupFaithMilestone.objects.filter(
            group=self.group,
        )

        self.assertEqual(milestones.count(), 2)

        self.assertTrue(
            milestones.filter(
                faith_milestone=self.faith_milestone1,
            ).exists()
        )
        self.assertTrue(
            milestones.filter(
                faith_milestone=self.faith_milestone2,
            ).exists()
        )


class TestRemoveGroupMilestoneView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )

        self.profile = self.user.profile
        self.profile.is_onboarded = True
        self.profile.save()

        self.client.login(
            email="testuser@example.com",
            password="password123",
        )

        # Create a group
        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            location_country="NG",
            location_city="Bauchi",
            slug="test-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        # Create a milestone and associate it with the group
        self.milestone = FaithMilestone.objects.create(
            title="Test Milestone",
            type="group",
            description="This is a test milestone.",
            author=self.profile,
        )

        self.group_faith_milestone = GroupFaithMilestone.objects.create(
            group=self.group,
            faith_milestone=self.milestone,
        )

    def test_remove_group_milestone_success(self):
        """
        Test the successful removal of a milestone from a group.
        """
        url = reverse(
            "groups:remove_group_milestone",
            kwargs={
                "milestone_id": self.milestone.id,
            },
        )
        response = self.client.post(url)

        # Check if the milestone was deleted
        self.assertEqual(GroupFaithMilestone.objects.count(), 0)

        # Ensure redirection to the group's detail page
        self.assertRedirects(
            response,
            self.group.get_absolute_url(),
        )

        # Check if the success message is displayed
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Group milestone removed.")

    def test_remove_group_milestone_not_found(self):
        """
        Test the removal of a non-existent milestone results in a 404 error.
        """
        non_existent_id = self.milestone.id + 1
        url = reverse(
            "groups:remove_group_milestone",
            kwargs={
                "milestone_id": non_existent_id,
            },
        )
        response = self.client.post(url)

        # Check if a 404 error is returned
        self.assertEqual(response.status_code, 404)

    def test_remove_group_milestone_unauthenticated(self):
        """
        Test that an unauthenticated user cannot remove a milestone.
        """
        self.client.logout()

        url = reverse(
            "groups:remove_group_milestone",
            kwargs={
                "milestone_id": self.milestone.id,
            },
        )

        response = self.client.post(url)

        # Check if redirected to login page
        self.assertRedirects(
            response,
            f"/accounts/login/?next={url}",
        )

    # def test_remove_group_milestone_permission(self):
    #     """
    #     Test that only authenticated users can remove a milestone.
    #     """
    #     # Create another user and login as them
    #     another_user = User.objects.create_user(
    #         email="anotheruser@example.com",
    #         password="password123",
    #     )

    #     self.client.login(
    #         email="anotheruser@example.com",
    #         password="password123",
    #     )

    #     url = reverse(
    #         "groups:remove_group_milestone",
    #         kwargs={
    #             "milestone_id": self.milestone.id,
    #         },
    #     )
    #     response = self.client.post(url)

    #     # Check if the response redirects back (not allowed to remove)
    #     self.assertRedirects(
    #         response,
    #         reverse(
    #             "groups:group_overview",
    #             kwargs={
    #                 "group_slug": self.group.slug,
    #             },
    #         ),
    #     )

    #     # Ensure a warning message is displayed
    #     messages = list(response.wsgi_request._messages)

    #     self.assertEqual(len(messages), 1)
    #     self.assertEqual(
    #         str(messages[0]),
    #         "You do not have permission to remove this milestone.",
    #     )


class TestGroupIndexView(TestCase):
    def setUp(self):
        """
        Set up test data for the group index view.
        """
        self.client = Client()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )
        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="testpassword",
        )
        self.user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="testpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile1 = self.user.profile
        self.profile2 = self.user2.profile
        self.profile3 = self.user3.profile

        self.profile1.is_onboarded = True
        self.profile1.role = "leader"
        self.profile1.save()

        self.profile2.is_onboarded = True
        self.profile2.first_name = "Moses"
        self.profile2.last_name = "Jacob"
        self.profile2.save()

        self.profile3.is_onboarded = True
        self.profile3.role = "leader"
        self.profile3.save()

        # Create groups
        self.group1 = Group.objects.create(
            leader=self.profile1,
            name="Alpha Group",
            location_country="GH",
            location_city="Accra",
            description="Group for alpha members.",
        )

        self.group2 = Group.objects.create(
            leader=self.profile2,
            name="Beta Group",
            parent=self.group1,
            location_country="NG",
            location_city="Kaduna",
            description="Group for beta members.",
        )

        self.group3 = Group.objects.create(
            leader=self.profile3,
            name="Gamma Group",
            parent=self.group1,
            location_country="NG",
            location_city="Kaduna",
            description="Group for gamma members.",
        )

        # Add members to groups
        self.group1.add_member(self.profile2)
        self.group1.add_member(self.profile3)

    def test_view_for_leader_without_group(self):
        """
        Test that the index view renders the correct template.
        """

        test_user = User.objects.create_user(
            email="example@example.com",
            password="password",
        )

        test_user.verified = True
        test_user.agreed_to_terms = True
        test_user.save()

        test_profile = test_user.profile

        test_profile.is_onboarded = True
        test_profile.role = "leader"
        test_profile.save()

        self.client.login(
            email=test_user.email,
            password="password",
        )

        response = self.client.get(reverse("groups:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "groups/pages/index.html")

        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_view_renders_correct_template(self):
        """
        Test that the index view renders the correct template.
        """
        response = self.client.get(reverse("groups:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "groups/pages/index.html")

    def test_view_filters_search(self):
        """
        Test that groups can be filtered by their name.
        """

        response = self.client.get(
            reverse("groups:index"),
            {
                "search": "Beta",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Beta Group")
        self.assertNotContains(response, "Gamma Group")
        self.assertNotContains(response, "Alpha Group")

    def test_view_filters_by_leader(self):
        """
        Test that groups can be filtered by leader.
        """

        response = self.client.get(
            reverse("groups:index"),
            {
                "leader": "Mos",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Beta Group")
        self.assertNotContains(response, "Gamma Group")
        self.assertNotContains(response, "Alpha Group")

    def test_pagination(self):
        """
        Test that pagination works correctly when more groups exist.
        """
        # Create more groups to trigger pagination
        for i in range(9):
            user = User.objects.create_user(
                email=f"looptestuser{i}@example.com",
                password="testpassword",
            )

            Group.objects.create(
                leader=user.profile,
                name=f"Loop Group {i}",
                parent=self.group1,
                location_country="NG",
                location_city="Kaduna",
                description="Group for gamma members.",
            )

        response = self.client.get(reverse("groups:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 6)

        # Test second page
        response = self.client.get(
            reverse("groups:index"),
            {
                "page": 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 6)

    def test_empty_form_does_not_filter(self):
        """
        Test that an empty form does not apply any filters.
        """
        response = self.client.get(reverse("groups:index"), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha Group")
        self.assertContains(response, "Beta Group")
        self.assertContains(response, "Gamma Group")

    def test_view_filters_by_location_country(self):
        """
        Test that groups can be filtered by location country.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "location_country": "GH",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha Group")
        self.assertNotContains(response, "Beta Group")
        self.assertNotContains(response, "Gamma Group")

    def test_view_filters_by_location_city(self):
        """
        Test that groups can be filtered by location city.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "location_city": "Accra",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha Group")
        self.assertNotContains(response, "Beta Group")

    def test_view_filters_by_skills(self):
        """
        Test that groups can be filtered by skills associated with the group.
        """
        skill = Skill.objects.create(
            title="Leadership",
            content="Leadership skill",
            author=self.profile1,
        )

        ProfileSkill.objects.create(
            profile=self.profile3,
            skill=skill,
        )

        response = self.client.get(
            reverse("groups:index"),
            {
                "skills": [skill.id],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha Group")
        self.assertNotContains(response, "Beta Group")
        self.assertNotContains(response, "Gamma Group")

    def test_view_filters_by_interests(self):
        """
        Test that groups can be filtered by interests associated with the group.
        """
        interest = Skill.objects.create(
            title="Leadership",
            content="Leadership skill",
            author=self.profile1,
        )

        ProfileInterest.objects.create(
            profile=self.profile3,
            interest=interest,
        )

        response = self.client.get(
            reverse("groups:index"),
            {
                "interests": [interest.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha Group")
        self.assertNotContains(response, "Beta Group")
        self.assertNotContains(response, "Gamma Group")

    def test_view_filters_by_vocations(self):
        """
        Test that groups can be filtered by vocations associated with the group.
        """
        vocation = Vocation.objects.create(
            title="Leadership",
            description="Leadership vocation",
            author=self.profile1,
        )

        ProfileVocation.objects.create(
            profile=self.profile3,
            vocation=vocation,
        )

        response = self.client.get(
            reverse("groups:index"),
            {
                "vocations": [vocation.id],
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Alpha Group")
        self.assertNotContains(response, "Beta Group")
        self.assertNotContains(response, "Gamma Group")

    def test_view_filters_by_mentorship_areas(self):
        """
        Test that groups can be filtered by mentorship areas associated with the group.
        """
        mentorship_area = MentorshipArea.objects.create(
            title="Leadership",
            content="Leadership mentorship_area",
            author=self.profile1,
        )

        ProfileMentorshipArea.objects.create(
            profile=self.profile3,
            mentorship_area=mentorship_area,
        )

        response = self.client.get(
            reverse("groups:index"),
            {
                "mentorship_areas": [mentorship_area.id],
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Alpha Group")
        self.assertNotContains(response, "Beta Group")
        self.assertNotContains(response, "Gamma Group")

    def test_view_filters_by_faith_milestones(self):
        """
        Test that profiles can be filtered by faith milestones.
        """
        # Create faith milestones
        faith_milestone1 = FaithMilestone.objects.create(
            title="Milestone 1",
            type="group",
            description="First faith milestone",
            author=self.profile1,
        )
        faith_milestone2 = FaithMilestone.objects.create(
            title="Milestone 2",
            type="group",
            description="Second faith milestone",
            author=self.profile1,
        )

        # Assign faith milestones to profiles
        GroupFaithMilestone.objects.create(
            faith_milestone=faith_milestone1,
            group=self.group1,
        )
        GroupFaithMilestone.objects.create(
            faith_milestone=faith_milestone2,
            group=self.group2,
        )

        response = self.client.get(
            reverse("groups:index"),
            {
                "faith_milestones": [
                    faith_milestone1.id,
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.group1.name)
        self.assertNotContains(response, self.group2.name)
        self.assertNotContains(response, self.group3.name)


class TestGroupIndexViewMembersFilter(TestCase):
    def setUp(self):
        """
        Set up test data for the group index view with members and their roles.
        """
        self.client = Client()

        # Create users
        self.user1 = User.objects.create_user(
            email="leader1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="leader2@example.com",
            password="password",
        )
        self.user3 = User.objects.create_user(
            email="member@example.com",
            password="password",
        )
        self.user4 = User.objects.create_user(
            email="mentor@example.com",
            password="password",
        )
        self.user5 = User.objects.create_user(
            email="trainer@example.com",
            password="password",
        )

        # Profiles with roles and facilitators
        self.profile1 = self.user1.profile
        self.profile1.role = "leader"
        self.profile1.is_onboarded = True
        self.profile1.is_skill_training_facilitator = True
        self.profile1.save()

        self.profile2 = self.user2.profile
        self.profile2.role = "leader"
        self.profile2.is_skill_training_facilitator = True
        self.profile2.save()

        self.profile3 = self.user3.profile
        self.profile3.role = "member"
        self.profile3.save()

        self.profile4 = self.user4.profile
        self.profile4.role = "external_person"
        self.profile4.is_movement_training_facilitator = True
        self.profile4.is_mentor = True
        self.profile4.save()

        self.profile5 = self.user5.profile
        self.profile5.save()

        # Create groups
        self.group1 = Group.objects.create(
            leader=self.profile1,
            name="Group 1",
            location_country="US",
            location_city="New York",
        )
        self.group2 = Group.objects.create(
            leader=self.profile2,
            name="Group 2",
            location_country="US",
            location_city="Boston",
        )

        # Add members to groups
        self.group1.add_member(self.profile2)
        self.group1.add_member(self.profile3)
        self.group1.add_member(self.profile4)

        self.group2.add_member(self.profile5)

        self.client.login(
            email=self.user1.email,
            password="password",
        )

    def test_filter_by_num_members(self):
        """
        Test that groups can be filtered by number of members.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "num_members": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group 1")
        self.assertNotContains(response, "Group 2")

    def test_filter_by_num_leaders(self):
        """
        Test that groups can be filtered by number of leaders.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "num_leaders": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group 1")
        self.assertNotContains(response, "Group 2")

    def test_filter_by_num_skill_trainers(self):
        """
        Test that groups can be filtered by number of skill trainers.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "num_skill_trainers": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group 1")
        self.assertNotContains(response, "Group 2")

    def test_filter_by_num_movement_trainers(self):
        """
        Test that groups can be filtered by number of movement trainers.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "num_movement_trainers": 1,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Group 1")
        self.assertNotContains(response, "Group 2")

    def test_filter_by_num_mentors(self):
        """
        Test that groups can be filtered by number of mentors.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "num_mentors": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group 1")
        self.assertNotContains(response, "Group 2")

    def test_filter_by_num_external_persons(self):
        """
        Test that groups can be filtered by number of external persons.
        """
        self.profile3.role = "external_person"
        self.profile3.save()

        response = self.client.get(
            reverse("groups:index"),
            {
                "num_external_persons": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group 1")
        self.assertNotContains(response, "Group 2")


class TestGroupIndexViewBasicFilters(TestCase):
    def setUp(self):
        """
        Set up test data for the group index view filters.
        """
        self.client = Client()

        # Create users
        self.user1 = User.objects.create_user(
            email="leader1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="leader2@example.com",
            password="password",
        )

        # Profiles with roles
        self.profile1 = self.user1.profile
        self.profile1.role = "leader"
        self.profile1.is_onboarded = True
        self.profile1.first_name = "Moses"
        self.profile1.last_name = "Jacob"
        self.profile1.save()

        self.profile2 = self.user2.profile
        self.profile2.role = "leader"
        self.profile2.is_onboarded = True
        self.profile2.save()

        # Create groups
        self.group1 = Group.objects.create(
            leader=self.profile1,
            name="Group Alpha",
            location_country="US",
            location_city="New York",
        )
        self.group2 = Group.objects.create(
            leader=self.profile2,
            name="Group Beta",
            location_country="NG",
            location_city="Bauchi",
        )

        self.client.login(
            email=self.user1.email,
            password="password",
        )

    def test_filter_by_location_country(self):
        """
        Test that groups can be filtered by location country.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "location_country": "US",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")

    def test_filter_by_location_city(self):
        """
        Test that groups can be filtered by location city.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "location_city": "New York",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")

    def test_filter_by_leader_first_name(self):
        """
        Test that groups can be filtered by leader's first name.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "leader": "Moses",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")

    def test_filter_by_leader_last_name(self):
        """
        Test that groups can be filtered by leader's last name.
        """
        self.profile1.last_name = "Smith"
        self.profile1.save()

        response = self.client.get(
            reverse("groups:index"),
            {
                "leader": "Smith",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")

    def test_combined_filters(self):
        """
        Test that groups can be filtered by multiple criteria.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "location_country": "USA",
                "location_city": "New York",
                "leader": "Mos",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")


class TestGroupIndexViewDemographicsFilters(TestCase):
    def setUp(self):
        """
        Set up test data for the group index view with members and their roles.
        """
        self.client = Client()

        # Create users
        self.user1 = User.objects.create_user(
            email="leader1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="leader2@example.com",
            password="password",
        )
        self.user3 = User.objects.create_user(
            email="member@example.com",
            password="password",
        )
        self.user4 = User.objects.create_user(
            email="mentor@example.com",
            password="password",
        )
        self.user5 = User.objects.create_user(
            email="trainer@example.com",
            password="password",
        )

        # Profiles with roles and facilitators
        self.profile1 = self.user1.profile
        self.profile1.role = "leader"
        self.profile1.is_onboarded = True
        self.profile1.is_skill_training_facilitator = True
        self.profile1.save()

        self.profile2 = self.user2.profile
        self.profile2.role = "leader"
        self.profile2.is_skill_training_facilitator = True
        self.profile2.save()

        self.profile3 = self.user3.profile
        self.profile3.role = "member"
        self.profile3.save()

        self.profile4 = self.user4.profile
        self.profile4.role = "external_person"
        self.profile4.is_movement_training_facilitator = True
        self.profile4.gender = "female"
        self.profile4.is_mentor = True
        self.profile4.save()

        self.profile5 = self.user5.profile
        self.profile5.save()

        # Create groups
        self.group1 = Group.objects.create(
            leader=self.profile1,
            name="Group 1",
            location_country="US",
            location_city="New York",
        )

        self.group2 = Group.objects.create(
            leader=self.profile2,
            name="Group 2",
            location_country="US",
            location_city="Boston",
        )

        # Add members to groups
        self.group1.add_member(self.profile2)
        self.group1.add_member(self.profile3)
        self.group1.add_member(self.profile4)

        self.group2.add_member(self.profile5)

        self.client.login(
            email=self.user1.email,
            password="password",
        )

    def test_filter_by_num_male_members(self):
        """
        Test that groups can be filtered by minimum number of male members.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "num_male_members": 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group 1")
        self.assertNotContains(response, "Group 2")

    def test_filter_by_num_female_members(self):
        """
        Test that groups can be filtered by minimum number of female members.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "num_female_members": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Group 2")
        self.assertContains(response, "Group 1")

    def test_filter_by_more_male_members(self):
        """
        Test that groups can be filtered to show groups with more male than female members.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "more_male_members": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group 1")
        self.assertContains(response, "Group 1")

    def test_filter_by_more_female_members(self):
        """
        Test that groups can be filtered to show groups with more female than male members.
        """
        self.profile2.gender = "female"
        self.profile2.save()
        self.profile3.gender = "female"
        self.profile3.save()
        self.profile4.gender = "female"
        self.profile4.save()

        response = self.client.get(
            reverse("groups:index"),
            {
                "more_female_members": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group 1")
        self.assertNotContains(response, "Group 2")

    def test_combined_demographics_filters(self):
        """
        Test that groups can be filtered by multiple demographics criteria.
        """
        self.profile2.gender = "female"
        self.profile2.save()
        self.profile3.gender = "female"
        self.profile3.save()
        self.profile4.gender = "female"
        self.profile4.save()

        response = self.client.get(
            reverse("groups:index"),
            {
                "num_female_members": 1,
                "more_female_members": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group 1")
        self.assertNotContains(response, "Group 2")


class TestGroupIndexViewSkillsInterestsFilters(TestCase):
    def setUp(self):
        """
        Set up test data for the group index view with skills and interests filters.
        """
        self.client = Client()

        # Create users
        self.user1 = User.objects.create_user(
            email="leader1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="leader2@example.com",
            password="password",
        )
        self.user3 = User.objects.create_user(
            email="leader3@example.com",
            password="password",
        )
        self.user4 = User.objects.create_user(
            email="leader4@example.com",
            password="password",
        )

        # Profiles with skills and interests
        self.profile1 = self.user1.profile
        self.profile1.role = "leader"
        self.profile1.is_onboarded = True
        self.profile1.save()

        self.profile2 = self.user2.profile
        self.profile2.role = "leader"
        self.profile2.is_skill_training_facilitator = True
        self.profile2.is_onboarded = True
        self.profile2.save()

        self.profile3 = self.user3.profile
        self.profile3.is_onboarded = True
        self.profile3.save()

        self.profile4 = self.user4.profile
        self.profile4.is_onboarded = True
        self.profile4.is_movement_training_facilitator = True
        self.profile4.save()

        # Create mock data for skills, interests and vocations
        self.skill1 = Skill.objects.create(
            title="Python",
            content="Content for a skill",
            author=self.profile1,
        )
        self.skill2 = Skill.objects.create(
            title="Django",
            content="Content for a skill",
            author=self.profile1,
        )

        self.vocation1 = Vocation.objects.create(
            title="Developer",
            description="Writes code",
            author=self.profile1,
        )

        # Create groups
        self.group1 = Group.objects.create(
            leader=self.profile1,
            name="Group Alpha",
            location_country="US",
            location_city="New York",
        )
        self.group2 = Group.objects.create(
            leader=self.profile2,
            name="Group Beta",
            location_country="NG",
            location_city="Bauchi",
        )

        # Assign skills and interests to members
        ProfileSkill.objects.create(
            profile=self.profile1,
            skill=self.skill1,
        )
        ProfileSkill.objects.create(
            profile=self.profile2,
            skill=self.skill2,
        )
        ProfileInterest.objects.create(
            profile=self.profile1,
            interest=self.skill2,
        )
        ProfileInterest.objects.create(
            profile=self.profile3,
            interest=self.skill1,
        )
        ProfileInterest.objects.create(
            profile=self.profile3,
            interest=self.skill2,
        )

        self.group1.add_member(self.profile2)
        self.group1.add_member(self.profile3)
        self.group2.add_member(self.profile4)

        self.client.login(
            email=self.user1.email,
            password="password",
        )

    def test_filter_by_skills(self):
        """
        Test that groups can be filtered by skills.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "skills": [self.skill2.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")

    def test_filter_by_interests(self):
        """
        Test that groups can be filtered by interests.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "interests": [
                    self.skill1.id,
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")

    def test_filter_by_unique_skills(self):
        """
        Test that groups can be filtered by no of unique skills.
        """

        response = self.client.get(
            reverse("groups:index"),
            {
                "unique_skills_count": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")

    def test_filter_by_unique_interests(self):
        """
        Test that groups can be filtered by no of unique interests.
        """

        response = self.client.get(
            reverse("groups:index"),
            {
                "unique_interests_count": 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")


class TestGroupIndexViewVocationsFilters(TestCase):
    def setUp(self):
        """
        Set up test data for the group index view with vocations filters.
        """
        self.client = Client()

        # Create users
        self.user1 = User.objects.create_user(
            email="leader1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="leader2@example.com",
            password="password",
        )
        self.user3 = User.objects.create_user(
            email="leader3@example.com",
            password="password",
        )
        self.user4 = User.objects.create_user(
            email="leader4@example.com",
            password="password",
        )

        # Profiles with vocations
        self.profile1 = self.user1.profile
        self.profile1.role = "leader"
        self.profile1.is_onboarded = True
        self.profile1.save()

        self.profile2 = self.user2.profile
        self.profile2.role = "leader"
        self.profile2.is_skill_training_facilitator = True
        self.profile2.is_onboarded = True
        self.profile2.save()

        self.profile3 = self.user3.profile
        self.profile3.is_onboarded = True
        self.profile3.save()

        self.profile4 = self.user4.profile
        self.profile4.is_onboarded = True
        self.profile4.is_movement_training_facilitator = True
        self.profile4.save()

        # Create mock data for vocations
        self.vocation1 = Vocation.objects.create(
            title="Python",
            description="Content for a vocation",
            author=self.profile1,
        )
        self.vocation2 = Vocation.objects.create(
            title="Django",
            description="Content for a vocation",
            author=self.profile1,
        )
        self.vocation3 = Vocation.objects.create(
            title="Developer",
            description="Writes code",
            author=self.profile1,
        )

        # Create groups
        self.group1 = Group.objects.create(
            leader=self.profile1,
            name="Group Alpha",
            location_country="US",
            location_city="New York",
        )
        self.group2 = Group.objects.create(
            leader=self.profile2,
            name="Group Beta",
            location_country="NG",
            location_city="Bauchi",
        )

        # Assign vocations to members
        ProfileVocation.objects.create(
            profile=self.profile1,
            vocation=self.vocation1,
        )
        ProfileVocation.objects.create(
            profile=self.profile2,
            vocation=self.vocation2,
        )
        ProfileVocation.objects.create(
            profile=self.profile1,
            vocation=self.vocation2,
        )
        ProfileVocation.objects.create(
            profile=self.profile3,
            vocation=self.vocation1,
        )
        ProfileVocation.objects.create(
            profile=self.profile3,
            vocation=self.vocation2,
        )

        self.group1.add_member(self.profile2)
        self.group1.add_member(self.profile3)
        self.group2.add_member(self.profile4)

        self.client.login(
            email=self.user1.email,
            password="password",
        )

    def test_filter_by_vocations(self):
        """
        Test that groups can be filtered by vocations.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "vocations": [self.vocation2.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")

    def test_filter_by_unique_vocations_count(self):
        """
        Test that groups can be filtered by no of unique vocations.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "unique_vocations_count": 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")


class TestGroupIndexViewMentorshipAreasFilters(TestCase):
    def setUp(self):
        """
        Set up test data for the group index view with mentorship_areas filters.
        """
        self.client = Client()

        # Create users
        self.user1 = User.objects.create_user(
            email="leader1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="leader2@example.com",
            password="password",
        )
        self.user3 = User.objects.create_user(
            email="leader3@example.com",
            password="password",
        )
        self.user4 = User.objects.create_user(
            email="leader4@example.com",
            password="password",
        )

        # Profiles with mentorship_areas
        self.profile1 = self.user1.profile
        self.profile1.role = "leader"
        self.profile1.is_onboarded = True
        self.profile1.save()

        self.profile2 = self.user2.profile
        self.profile2.role = "leader"
        self.profile2.is_skill_training_facilitator = True
        self.profile2.is_onboarded = True
        self.profile2.save()

        self.profile3 = self.user3.profile
        self.profile3.is_onboarded = True
        self.profile3.save()

        self.profile4 = self.user4.profile
        self.profile4.is_onboarded = True
        self.profile4.is_movement_training_facilitator = True
        self.profile4.save()

        # Create mock data for mentorship_areas
        self.mentorship_area1 = MentorshipArea.objects.create(
            title="Python",
            content="Content for a mentorship_area",
            author=self.profile1,
        )
        self.mentorship_area2 = MentorshipArea.objects.create(
            title="Django",
            content="Content for a mentorship_area",
            author=self.profile1,
        )
        self.mentorship_area3 = MentorshipArea.objects.create(
            title="Developer",
            content="Writes code",
            author=self.profile1,
        )

        # Create groups
        self.group1 = Group.objects.create(
            leader=self.profile1,
            name="Group Alpha",
            location_country="US",
            location_city="New York",
        )
        self.group2 = Group.objects.create(
            leader=self.profile2,
            name="Group Beta",
            location_country="NG",
            location_city="Bauchi",
        )

        # Assign mentorship_areas to members
        ProfileMentorshipArea.objects.create(
            profile=self.profile2,
            mentorship_area=self.mentorship_area1,
        )
        ProfileMentorshipArea.objects.create(
            profile=self.profile2,
            mentorship_area=self.mentorship_area2,
        )
        ProfileMentorshipArea.objects.create(
            profile=self.profile2,
            mentorship_area=self.mentorship_area3,
        )
        ProfileMentorshipArea.objects.create(
            profile=self.profile3,
            mentorship_area=self.mentorship_area2,
        )

        self.group1.add_member(self.profile2)
        self.group1.add_member(self.profile3)
        self.group2.add_member(self.profile4)

        self.client.login(
            email=self.user1.email,
            password="password",
        )

    def test_filter_by_mentorship_areas(self):
        """
        Test that groups can be filtered by mentorship_areas.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "mentorship_areas": [self.mentorship_area2.id],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")

    def test_filter_by_unique_mentorship_areas_count(self):
        """
        Test that groups can be filtered by no of unique mentorship_areas.
        """
        response = self.client.get(
            reverse("groups:index"),
            {
                "unique_mentorship_areas_count": 3,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group Alpha")
        self.assertNotContains(response, "Group Beta")
