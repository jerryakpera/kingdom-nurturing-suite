from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import Client, TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from kns.accounts.utils import generate_verification_token
from kns.core.models import MakeLeaderActionApproval
from kns.core.utils import log_this
from kns.custom_user.models import User
from kns.groups.models import Group
from kns.profiles.models import Profile

from ..models import FAQ


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


class TestMakeLeaderApprovalView(TestCase):
    def setUp(self):
        # Set up the initial data
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )
        self.profile = self.user.profile

        self.profile.is_onboarded = True
        self.profile.save()

        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            description="A test group.",
        )

        self.approval_request = MakeLeaderActionApproval.objects.create(
            new_leader=self.profile,
            created_by=self.profile,
            group_created_for=self.group,
            action_type="change_role_to_leader",
            status="pending",
        )

        self.token = generate_verification_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))

    def test_approve_make_leader_success(self):
        """
        Test that a valid approval request is successfully processed.
        """
        response = self.client.get(
            reverse(
                "core:approve_make_leader_action",
                kwargs={
                    "action_approval_id": self.approval_request.pk,
                    "uidb64": self.uid,
                    "token": self.token,
                },
            )
        )

        self.approval_request.refresh_from_db()

        self.assertEqual(self.approval_request.status, "approved")
        self.assertIsNotNone(self.approval_request.approved_at)

        messages = list(get_messages(response.wsgi_request))

        self.assertTrue(
            any("is now a leader" in str(message) for message in messages),
        )

    def test_invalid_token(self):
        """
        Test that an invalid token does not approve the request.
        """
        invalid_token = "invalid-token"
        response = self.client.get(
            reverse(
                "core:approve_make_leader_action",
                kwargs={
                    "action_approval_id": self.approval_request.pk,
                    "uidb64": self.uid,
                    "token": invalid_token,
                },
            )
        )

        self.approval_request.refresh_from_db()
        self.assertEqual(self.approval_request.status, "pending")

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 302)
        self.assertTrue("You cannot complete this action" in str(messages[0]))

    def test_request_no_longer_valid(self):
        """
        Test that an already approved or expired request cannot be approved again.
        """
        self.approval_request.status = "approved"
        self.approval_request.save()

        response = self.client.get(
            reverse(
                "core:approve_make_leader_action",
                kwargs={
                    "action_approval_id": self.approval_request.pk,
                    "uidb64": self.uid,
                    "token": self.token,
                },
            )
        )

        self.approval_request.refresh_from_db()
        self.assertEqual(self.approval_request.status, "approved")

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            "This request is no longer valid and cannot be accepted."
            in str(messages[0]),
        )

    def test_user_not_group_leader(self):
        """
        Test that a user who is not the group leader cannot approve the request.
        """
        another_user = User.objects.create_user(
            email="not_leader@example.com",
            password="password",
        )

        another_profile = another_user.profile

        self.group.add_member(another_profile)

        Group.objects.create(
            leader=another_profile,
            name="Test Group 2",
            slug="test-group-2",
            parent=self.group,
            description="A test group 2 description.",
        )

        self.token = generate_verification_token(another_user)
        self.uid = urlsafe_base64_encode(force_bytes(another_user.pk))

        response = self.client.get(
            reverse(
                "core:approve_make_leader_action",
                kwargs={
                    "action_approval_id": self.approval_request.pk,
                    "uidb64": self.uid,
                    "token": self.token,
                },
            )
        )

        self.approval_request.refresh_from_db()
        self.assertEqual(self.approval_request.status, "pending")

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            "You cannot complete this action" in str(messages[0]),
        )


class TestMakeLeaderApprovalNotificationView(TestCase):
    def setUp(self):
        # Set up the initial data
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )
        self.profile = self.user.profile

        self.profile.is_onboarded = True
        self.profile.save()

        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            description="A test group.",
        )

        self.approval_request = MakeLeaderActionApproval.objects.create(
            new_leader=self.profile,
            created_by=self.profile,
            group_created_for=self.group,
            action_type="change_role_to_leader",
            status="pending",
        )

    def test_approve_make_leader_success(self):
        """
        Test that a valid approval request is successfully processed.
        """

        self.client.login(
            email=self.user.email,
            password="password",
        )

        response = self.client.get(
            reverse(
                "core:approve_make_leader_action_notification",
                kwargs={
                    "action_approval_id": self.approval_request.pk,
                },
            )
        )

        self.approval_request.refresh_from_db()

        self.assertEqual(self.approval_request.status, "approved")
        self.assertIsNotNone(self.approval_request.approved_at)

        messages = list(get_messages(response.wsgi_request))

        self.assertTrue(
            any("is now a leader" in str(message) for message in messages),
        )

    def test_request_no_longer_valid(self):
        """
        Test that an already approved or expired request cannot be approved again.
        """
        self.client.login(
            email=self.user.email,
            password="password",
        )

        self.approval_request.status = "approved"
        self.approval_request.save()

        response = self.client.get(
            reverse(
                "core:approve_make_leader_action_notification",
                kwargs={
                    "action_approval_id": self.approval_request.pk,
                },
            )
        )

        self.approval_request.refresh_from_db()
        self.assertEqual(self.approval_request.status, "approved")

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            "This request is no longer valid and cannot be accepted."
            in str(messages[0]),
        )

    def test_user_not_group_leader(self):
        """
        Test that a user who is not the group leader cannot approve the request.
        """

        another_user = User.objects.create_user(
            email="not_leader@example.com",
            password="password",
        )

        another_profile = another_user.profile
        another_profile.is_onboarded = True

        another_profile.save()

        self.group.add_member(another_profile)

        self.client.login(
            email=another_user.email,
            password="password",
        )

        Group.objects.create(
            leader=another_profile,
            name="Test Group 2",
            slug="test-group-2",
            parent=self.group,
            description="A test group 2 description.",
        )

        response = self.client.get(
            reverse(
                "core:approve_make_leader_action_notification",
                kwargs={
                    "action_approval_id": self.approval_request.pk,
                },
            )
        )

        self.approval_request.refresh_from_db()
        self.assertEqual(
            self.approval_request.status,
            "pending",
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            "You cannot complete this action" in str(messages[0]),
        )
