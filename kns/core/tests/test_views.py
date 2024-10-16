from django.shortcuts import reverse
from django.test import Client, TestCase

from kns.custom_user.models import User
from kns.groups.models import Group
from kns.onboarding.models import ProfileCompletion

from ..models import FAQ, Notification, NotificationRecipient


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

        # Set up some FAQ data for testing
        FAQ.objects.create(
            question="What is the Kingdom Nurturing Suite (KNS)?",
            answer="A comprehensive collection of tools for DMM.",
        )

        FAQ.objects.create(
            question="How can I register a new DBS group in KNS?",
            answer="Register a new DBS group through the KNS web app.",
        )

    def test_index_response(self):
        """
        An user gets a valid response.
        """
        response = self.client.get(reverse("core:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/pages/index.html")

    def test_about_response(self):
        """
        An user gets a valid response.
        """
        response = self.client.get(reverse("core:about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/pages/about.html")

    def test_faqs_response(self):
        """
        An user gets a valid response and sees the FAQ content.
        """
        response = self.client.get(reverse("core:faqs"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/pages/faqs.html")

        # Check if the FAQs are being passed to the context
        self.assertIn("faqs", response.context)

    def test_submit_ticket_response(self):
        """
        An user gets a valid response.
        """
        response = self.client.get(reverse("core:submit_ticket"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "core/pages/submit_ticket.html",
        )

    def test_contact_response(self):
        """
        An user gets a valid response.
        """
        response = self.client.get(reverse("core:contact"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "core/pages/contact.html",
        )


class TestCoreIndexView(TestCase):
    def setUp(self):
        self.client = Client()

        # Set up user and profile data
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.profile = self.user.profile
        self.profile.is_onboarded = True
        self.profile.save()

        # Create a ProfileCompletion instance
        self.profile_completion = ProfileCompletion.objects.create(
            profile=self.profile,
        )

        # Create another user for the second group leader
        self.user2 = User.objects.create_user(
            email="anotheruser@example.com",
            password="password123",
        )
        self.profile2 = self.user2.profile
        self.profile2.is_onboarded = True
        self.profile2.save()

        # Create another user for the second group leader
        self.user3 = User.objects.create_user(
            email="thirduser@example.com",
            password="password133",
        )
        self.profile3 = self.user3.profile
        self.profile3.is_onboarded = True
        self.profile3.save()

        # Create groups for testing
        self.group1 = Group.objects.create(
            name="City Group",
            leader=self.profile,
            location_country="US",
            location_city="New York",
        )
        self.group2 = Group.objects.create(
            name="Country Group",
            leader=self.profile2,
            location_country="US",
            location_city="Boston",
            parent=self.group1,
        )
        self.group3 = Group.objects.create(
            name="Country Group 3",
            leader=self.profile3,
            location_country="US",
            location_city="Boston",
            parent=self.group1,
        )

        # Add members to the groups (if applicable)
        self.group1.add_member(self.profile2)

        # Log the user in
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )

    def test_index_response_unauthenticated(self):
        """
        An unauthenticated user should get a valid response without
        profile_completion in the context.
        """
        self.client.logout()
        response = self.client.get(reverse("core:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "core/pages/index.html",
        )

        # Check that profile_completion is not in the context
        self.assertNotIn(
            "profile_completion",
            response.context,
        )

    def test_index_response_authenticated_with_profile_completion(self):
        """
        An authenticated user with profile completion should get a valid response
        and have profile_completion and close_groups in the context.
        """
        # Log the user in
        self.client.login(
            email=self.profile3.email,
            password="password123",
        )

        response = self.client.get(reverse("core:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "core/pages/index.html",
        )

        # Check that the profile_completion object is passed in the context
        self.assertIn("profile_completion", response.context)
        self.assertEqual(
            response.context["profile_completion"],
            self.profile_completion,
        )

        # Check for close_groups in the context
        self.assertIn("close_groups", response.context)


class TestNotificationViews(TestCase):
    def setUp(self):
        self.client = Client()

        # Set up user and profile data
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )

        self.profile = self.user.profile
        self.profile.is_onboarded = True
        self.profile.save()

        # Create a ProfileCompletion instance
        self.profile_completion = ProfileCompletion.objects.create(
            profile=self.profile,
        )

        # Create a notification for the user
        self.notification = Notification.objects.create(
            notification_type="group_move",
            title="Group Moved",
            message="Your group has been moved to a new location.",
            link="https://example.com/group/1",
            sender=self.profile,
        )

        # Create a notification recipient
        NotificationRecipient.objects.create(
            notification=self.notification,
            recipient=self.profile,
            is_read=False,
        )

        # Log the user in
        self.client.login(
            email="testuser@example.com",
            password="password123",
        )

    def test_mark_notification_and_redirect(self):
        """
        A logged-in user marks a notification as read and is redirected to its link.
        """
        response = self.client.get(
            reverse(
                "core:mark_notification_and_redirect",
                args=[self.notification.id],
            )
        )

        # Ensure the response is a redirect, without fetching the final response
        self.assertRedirects(
            response,
            self.notification.link,
            fetch_redirect_response=False,
        )

        # Verify that the notification was marked as read
        recipient_record = NotificationRecipient.objects.get(
            recipient=self.profile,
            notification=self.notification,
        )

        self.assertTrue(recipient_record.is_read)

    def test_mark_notification_unauthenticated(self):
        """
        An unauthenticated user is redirected to the login page when trying to mark a notification.
        """
        self.client.logout()
        response = self.client.get(
            reverse(
                "core:mark_notification_and_redirect",
                args=[self.notification.id],
            )
        )

        # Check if the user is redirected to the login page
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse(
                'core:mark_notification_and_redirect',
                args=[self.notification.id],
            )}",
        )

    def test_mark_nonexistent_notification(self):
        """
        Attempting to mark a nonexistent notification should return a 404 error.
        """
        response = self.client.get(
            reverse(
                "core:mark_notification_and_redirect",
                args=[999],
            )
        )

        self.assertEqual(response.status_code, 404)
