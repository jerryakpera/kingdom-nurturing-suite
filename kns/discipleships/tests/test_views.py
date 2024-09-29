from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.discipleships.models import Discipleship
from kns.groups.models import Group
from kns.groups.tests import test_constants


class TestProfileDiscipleshipsView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.slug = "test-user"
        self.profile.is_onboarded = True

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        self.profile.save()

        self.other_user.verified = True
        self.other_user.agreed_to_terms = True

        self.other_user.save()

        self.other_profile = self.other_user.profile

        # Create a group
        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.group.add_member(self.other_profile)

    def test_profile_discipleships_view_loads_correctly(self):
        """
        Test that the profile_discipleships view loads correctly
        and renders the form.
        """
        url = reverse(
            "discipleships:profile_discipleships",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "profiles/pages/profile_discipleships.html",
        )
        self.assertIn(
            "group_member_discipleship_form",
            response.context,
        )

    def test_profile_discipleships_view_with_invalid_slug(self):
        """
        Test that the profile_discipleships view returns a 404 error
        when the profile slug does not exist.
        """
        url = reverse(
            "discipleships:profile_discipleships",
            kwargs={
                "profile_slug": "invalid-slug",
            },
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_profile_discipleships_form_submission(self):
        """
        Test that submitting the form in the profile_discipleships view
        processes correctly.
        """
        url = reverse(
            "discipleships:profile_discipleships",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        response = self.client.post(
            url,
            data={
                "disciple": self.profile.id,
            },
        )

        # Since this view only renders the form and does not handle form submission,
        # we expect the response to still be 200, and no changes to have occurred.
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "group_member_discipleship_form",
            response.context,
        )

    def test_profile_discipleships_view_post_success(self):
        """
        Test that a valid POST request adds a new disciple
        and redirects correctly.
        """
        url = reverse(
            "discipleships:profile_discipleships",
            kwargs={"profile_slug": self.profile.slug},
        )
        data = {
            "disciple": self.other_profile.id,
        }

        response = self.client.post(url, data=data)

        # Check if the disciple was added
        self.assertTrue(
            Discipleship.objects.filter(
                disciple=self.other_profile,
                discipler=self.profile,
            ).exists()
        )

        # Check if the response redirects
        self.assertEqual(response.status_code, 200)

        # Check if the success message is in the messages
        messages_list = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "Disciple added to your group members",
        )

    def test_profile_discipleships_view_post_duplicate_disciple(self):
        """
        Test that trying to add an existing disciple shows a warning message.
        """
        # First, create an existing discipleship
        Discipleship.objects.create(
            disciple=self.other_profile,
            discipler=self.profile,
            group="Group member",
            author=self.profile,
        )

        url = reverse(
            "discipleships:profile_discipleships",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        data = {
            "disciple": self.other_profile.id,
        }

        response = self.client.post(url, data=data)

        # Check that no new discipleship is created
        self.assertEqual(
            Discipleship.objects.filter(
                disciple=self.other_profile,
                discipler=self.profile,
            ).count(),
            1,
        )

        # Check if the response redirects
        self.assertEqual(response.status_code, 200)

        # Check if the warning message is in the messages
        messages_list = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "This person is already a disciple",
        )

    def test_profile_discipleships_view_post_invalid_form(self):
        """
        Test that submitting an invalid form does not create a disciple
        and stays on the same page.
        """
        url = reverse(
            "discipleships:profile_discipleships",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        data = {
            "disciple": "",  # Invalid data
        }

        response = self.client.post(url, data=data)

        # Check that no discipleship is created
        self.assertFalse(
            Discipleship.objects.filter(
                discipler=self.profile,
            ).exists()
        )

        # Check if the response redirects back to the same page
        self.assertEqual(response.status_code, 200)

        # Since no disciple was added, check that the form errors are correctly handled
        messages_list = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages_list), 0)


class TestMoveDiscipleshipViews(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.client.login(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile
        self.profile.is_onboarded = True
        self.profile.save()

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )
        self.other_profile = self.other_user.profile

        # Create a discipleship instance for testing
        self.discipleship = Discipleship.objects.create(
            disciple=self.other_profile,
            discipler=self.profile,
            author=self.profile,
            group="group_member",
        )

    def test_move_to_group_member(self):
        url = reverse(
            "discipleships:move_to_group_member",
            kwargs={
                "discipleship_id": self.discipleship.id,
            },
        )

        response = self.client.post(url)

        # Check if the discipleship was moved to 'group_member'
        self.assertTrue(
            Discipleship.objects.filter(
                disciple=self.other_profile,
                discipler=self.profile,
                group="group_member",
            ).exists()
        )

        # Check if the response redirects correctly
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            f"{self.other_profile.get_full_name()} moved to group members.",
        )

    def test_move_to_first_12(self):
        url = reverse(
            "discipleships:move_to_first_12",
            kwargs={
                "discipleship_id": self.discipleship.id,
            },
        )

        response = self.client.post(url)

        # Check if the discipleship was moved to 'first_12'
        self.assertTrue(
            Discipleship.objects.filter(
                disciple=self.other_profile,
                discipler=self.profile,
                group="first_12",
            ).exists()
        )

        # Check if the response redirects correctly
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            f"{self.other_profile.get_full_name()} moved to first 12.",
        )

    def test_move_to_first_3(self):
        url = reverse(
            "discipleships:move_to_first_3",
            kwargs={
                "discipleship_id": self.discipleship.id,
            },
        )

        response = self.client.post(url)

        # Check if the discipleship was moved to 'first_3'
        self.assertTrue(
            Discipleship.objects.filter(
                disciple=self.other_profile,
                discipler=self.profile,
                group="first_3",
            ).exists()
        )

        # Check if the response redirects correctly
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            f"{self.other_profile.get_full_name()} moved to first 3.",
        )

    def test_move_to_sent_forth(self):
        url = reverse(
            "discipleships:move_to_sent_forth",
            kwargs={
                "discipleship_id": self.discipleship.id,
            },
        )

        response = self.client.post(url)

        # Check if the discipleship was moved to 'sent_forth'
        self.assertTrue(
            Discipleship.objects.filter(
                disciple=self.other_profile,
                discipler=self.profile,
                group="sent_forth",
            ).exists()
        )

        # Check if the response redirects correctly
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            f"{self.other_profile.get_full_name()} sent forth.",
        )

    def test_move_disallow_if_not_author(self):
        # Create another discipleship with different author
        another_discipleship = Discipleship.objects.create(
            disciple=self.other_profile,
            discipler=self.profile,
            author=self.other_profile,
            group="group_member",
        )

        url = reverse(
            "discipleships:move_to_group_member",
            kwargs={
                "discipleship_id": another_discipleship.id,
            },
        )

        response = self.client.post(url)

        # Check if the response redirects back to the discipler's discipleships page with an error
        self.assertEqual(response.status_code, 302)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "You cannot complete this action",
        )

    def test_move_to_group_member_not_author(self):
        self.other_profile = self.other_user.profile
        self.other_profile.is_onboarded = True
        self.other_profile.save()

        self.client.login(
            email=self.other_user.email,
            password="password",
        )

        url = reverse(
            "discipleships:move_to_group_member",
            kwargs={
                "discipleship_id": self.discipleship.id,
            },
        )

        response = self.client.post(url)

        # Check if the response redirects correctly
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "You cannot complete this action",
        )

    def test_move_to_first_12_not_author(self):
        self.other_profile = self.other_user.profile
        self.other_profile.is_onboarded = True
        self.other_profile.save()

        self.client.login(
            email=self.other_user.email,
            password="password",
        )

        url = reverse(
            "discipleships:move_to_first_12",
            kwargs={
                "discipleship_id": self.discipleship.id,
            },
        )

        response = self.client.post(url)

        # Check if the response redirects correctly
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages_list = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "You cannot complete this action",
        )

    def test_move_to_first_3_not_author(self):
        self.other_profile = self.other_user.profile
        self.other_profile.is_onboarded = True
        self.other_profile.save()

        self.client.login(
            email=self.other_user.email,
            password="password",
        )

        url = reverse(
            "discipleships:move_to_first_3",
            kwargs={
                "discipleship_id": self.discipleship.id,
            },
        )

        response = self.client.post(url)

        # Check if the response redirects correctly
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "You cannot complete this action",
        )

    def test_move_to_sent_forth_not_author(self):
        self.other_profile = self.other_user.profile
        self.other_profile.is_onboarded = True
        self.other_profile.save()

        self.client.login(
            email=self.other_user.email,
            password="password",
        )

        self.other_profile = self.other_user.profile
        self.other_profile.is_onboarded = True
        self.other_profile.save()

        url = reverse(
            "discipleships:move_to_sent_forth",
            kwargs={
                "discipleship_id": self.discipleship.id,
            },
        )

        response = self.client.post(url)

        # Check if the response redirects correctly
        self.assertEqual(response.status_code, 302)

        # Check if the success message is in the messages
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "You cannot complete this action",
        )
