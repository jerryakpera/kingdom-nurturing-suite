from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from kns.custom_user.models import User
from kns.discipleships.models import Discipleship
from kns.groups.models import Group
from kns.groups.tests import test_constants


class TestIndexView(TestCase):
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

        # Set up a profile for the user
        self.profile = self.user.profile
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.is_onboarded = True
        self.profile.save()

        # Create groups for testing
        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            description="A test group",
        )

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="otherpassword",
        )
        self.other_profile = self.other_user.profile
        self.other_profile.first_name = "Jane"
        self.other_profile.last_name = "Pritchet"
        self.other_profile.save()

        self.group.add_member(self.other_profile)

        # Create discipleships for testing
        self.discipleship1 = Discipleship.objects.create(
            disciple=self.other_profile,
            discipler=self.profile,
            group="group_member",
            author=self.profile,
        )

        self.discipleship2 = Discipleship.objects.create(
            disciple=self.profile,
            discipler=self.other_profile,
            group="first_12",
            author=self.other_profile,
        )

    def test_index_view_loads_correctly(self):
        """
        Test that the index view loads correctly and renders the filter form.
        """
        url = reverse("discipleships:index")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "discipleships/pages/index.html",
        )
        self.assertIn("filter_form", response.context)

    def test_index_view_with_search_query(self):
        """
        Test that the index view applies search filters correctly.
        """
        url = reverse("discipleships:index")
        response = self.client.get(
            url,
            {
                "search": "John",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.discipleship1,
            response.context["page_obj"],
        )

    def test_index_view_with_ongoing_status_filter(self):
        """
        Test that the index view filters discipleships by status.
        """

        self.discipleship1.completed_at = timezone.now()
        self.discipleship1.save()

        url = reverse("discipleships:index")
        response = self.client.get(
            url,
            {
                "filter_status": "ongoing",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            self.discipleship1,
            response.context["page_obj"],
        )
        self.assertIn(
            self.discipleship2,
            response.context["page_obj"],
        )

    def test_index_view_with_completed_status_filter(self):
        """
        Test that the index view filters discipleships by status.
        """

        self.discipleship1.completed_at = timezone.now()
        self.discipleship1.save()

        url = reverse("discipleships:index")
        response = self.client.get(
            url,
            {
                "filter_status": "completed",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.discipleship1,
            response.context["page_obj"],
        )
        self.assertNotIn(
            self.discipleship2,
            response.context["page_obj"],
        )

    def test_index_view_with_group_filter(self):
        """
        Test that the index view filters discipleships by group.
        """
        url = reverse("discipleships:index")
        response = self.client.get(
            url,
            {
                "filter_group": "group_member",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.discipleship1,
            response.context["page_obj"],
        )
        self.assertNotIn(
            self.discipleship2,
            response.context["page_obj"],
        )

    def test_index_view_with_multiple_filters(self):
        """Test that the index view applies multiple filters correctly."""
        url = reverse("discipleships:index")
        response = self.client.get(
            url,
            {
                "search": "John",
                "filter_status": "ongoing",
                "filter_group": "first_12",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.discipleship2,
            response.context["page_obj"],
        )
        self.assertNotIn(
            self.discipleship1,
            response.context["page_obj"],
        )

    def test_index_view_pagination(self):
        """
        Test that the index view paginates the list of discipleships correctly.
        """
        # Create enough discipleships to require multiple pages
        for i in range(15):
            user = User.objects.create_user(
                email=f"testuser{i}@example.com",
                password="testpassword",
            )
            disciples_profile = user.profile

            self.group.add_member(disciples_profile)

            Discipleship.objects.create(
                disciple=disciples_profile,
                discipler=self.profile,
                group="group_member",
                author=self.profile,
            )

        # Ensure pagination is working correctly by checking the number of items per page
        url = reverse("discipleships:index")
        response = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 6)

        # Test the second page
        response = self.client.get(url, {"page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 6)

        # Check if there are more pages
        paginator = response.context["page_obj"].paginator
        self.assertEqual(paginator.num_pages, 3)


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
            "discipleships/pages/profile_discipleships.html",
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
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.save()

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        self.other_profile = self.other_user.profile
        self.other_profile.first_name = "James"
        self.other_profile.last_name = "Pilot"
        self.other_profile.save()

        # Create a discipleship instance for testing
        self.discipleship = Discipleship.objects.create(
            disciple=self.other_profile,
            discipler=self.profile,
            author=self.profile,
            group="group_member",
        )

    def test_move_to_group_member(self):
        url = reverse(
            "discipleships:move_to_discipleship_group",
            kwargs={
                "discipleship_id": self.discipleship.id,
                "new_group": "group_member",
            },
        )

        response = self.client.post(url)

        self.assertTrue(
            Discipleship.objects.filter(
                disciple=self.other_profile,
                discipler=self.profile,
                group="group_member",
            ).exists()
        )
        self.assertEqual(response.status_code, 302)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            f"{self.other_profile.get_full_name()} moved to your Group member discipleship group.",
        )

    def test_move_to_first_12(self):
        url = reverse(
            "discipleships:move_to_discipleship_group",
            kwargs={
                "discipleship_id": self.discipleship.id,
                "new_group": "first_12",
            },
        )

        response = self.client.post(url)

        self.assertTrue(
            Discipleship.objects.filter(
                disciple=self.other_profile,
                discipler=self.profile,
                group="first_12",
            ).exists()
        )
        self.assertEqual(response.status_code, 302)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            f"{self.other_profile.get_full_name()} moved to your First 12 discipleship group.",
        )

    def test_move_to_first_3(self):
        url = reverse(
            "discipleships:move_to_discipleship_group",
            kwargs={
                "discipleship_id": self.discipleship.id,
                "new_group": "first_3",
            },
        )

        response = self.client.post(url)

        self.assertTrue(
            Discipleship.objects.filter(
                disciple=self.other_profile,
                discipler=self.profile,
                group="first_3",
            ).exists()
        )
        self.assertEqual(response.status_code, 302)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            f"{self.other_profile.get_full_name()} moved to your First 3 discipleship group.",
        )

    def test_move_to_sent_forth(self):
        url = reverse(
            "discipleships:move_to_discipleship_group",
            kwargs={
                "discipleship_id": self.discipleship.id,
                "new_group": "sent_forth",
            },
        )

        response = self.client.post(url)

        self.assertTrue(
            Discipleship.objects.filter(
                disciple=self.other_profile,
                discipler=self.profile,
                group="sent_forth",
            ).exists()
        )
        self.assertEqual(response.status_code, 302)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            f"{self.other_profile.get_full_name()} moved to your Sent forth discipleship group.",
        )

    def test_move_disallow_if_not_author(self):
        another_discipleship = Discipleship.objects.create(
            disciple=self.other_profile,
            discipler=self.profile,
            author=self.other_profile,
            group="group_member",
        )

        url = reverse(
            "discipleships:move_to_discipleship_group",
            kwargs={
                "discipleship_id": another_discipleship.id,
                "new_group": "group_member",
            },
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "You cannot complete this action",
        )

    def test_move_not_author(self):
        # Test moving to different groups as another user
        self.other_profile.is_onboarded = True
        self.other_profile.save()

        self.client.login(
            email=self.other_user.email,
            password="password",
        )

        url = reverse(
            "discipleships:move_to_discipleship_group",
            kwargs={
                "discipleship_id": self.discipleship.id,
                "new_group": "first_12",
            },
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        messages_list = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            str(messages_list[0]),
            "You cannot complete this action",
        )


class TestDiscipleshipHistoryView(TestCase):
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
            password="otherpassword",
        )
        self.other_profile = self.other_user.profile
        self.other_profile.is_onboarded = True
        self.other_profile.save()

        # Create discipleship instance for testing
        self.discipleship = Discipleship.objects.create(
            disciple=self.other_profile,
            discipler=self.profile,
            author=self.profile,
            group="group_member",
            slug="test-discipleship",
        )

        # Create additional discipleships for history testing
        self.discipleship_history = Discipleship.objects.create(
            disciple=self.other_profile,
            discipler=self.profile,
            author=self.profile,
            group="first_12",
            slug="test-discipleship-history",
        )

    def test_discipleship_history_view_loads_correctly(self):
        """
        Test that the discipleship_history view loads correctly
        and renders the history template.
        """
        url = reverse(
            "discipleships:discipleship_history",
            kwargs={"discipleship_slug": self.discipleship.slug},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "discipleships/pages/history.html",
        )
        self.assertIn("discipleship", response.context)
        self.assertIn("discipleships", response.context)

    def test_discipleship_history_view_with_invalid_slug(self):
        """
        Test that the discipleship_history view returns a 404 error
        when the discipleship slug does not exist.
        """
        url = reverse(
            "discipleships:discipleship_history",
            kwargs={"discipleship_slug": "invalid-slug"},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_discipleship_history_view_with_correct_history(self):
        """
        Test that the discipleship_history view retrieves the correct history
        for the discipleship.
        """
        url = reverse(
            "discipleships:discipleship_history",
            kwargs={"discipleship_slug": self.discipleship.slug},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.discipleship, response.context["discipleships"])
        self.assertEqual(len(response.context["discipleships"]), 2)  # Check count

    def test_discipleship_history_view_for_nonexistent_discipleship(self):
        """
        Test that the view handles a nonexistent discipleship gracefully.
        """
        # Create a discipleship with a different slug
        non_existent_slug = "nonexistent-discipleship"
        url = reverse(
            "discipleships:discipleship_history",
            kwargs={"discipleship_slug": non_existent_slug},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
