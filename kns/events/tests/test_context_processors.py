from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from kns.custom_user.models import User
from kns.events.context_processors import event_context
from kns.events.models import Event


class TestEventContextProcessor(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Create a user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass",
        )
        self.profile = self.user.profile
        self.profile.is_onboarded = True
        self.profile.save()

        # Create a sample event
        self.event = Event.objects.create(
            title="Test Event",
            summary="This is a test event.",
            description="Detailed description of the test event.",
            start_date="2024-01-01",
            end_date="2024-01-02",
            location_country="NG",
            location_city="Lagos",
            author=self.profile,
        )

    def test_event_context_event_not_found(self):
        """
        Test that no event data is returned if the event is not found.
        """
        request = self.factory.get("/events/non-existent-event/")
        request.resolver_match = MagicMock(
            kwargs={
                "event_slug": "non-existent-event",
            },
        )
        request.user = self.user

        context = event_context(request)

        self.assertIsNone(context["event"])
        self.assertFalse(context["can_edit_event"])

    def test_event_context_user_not_authenticated(self):
        """
        Test that 'can_edit_event' is False if the user is not authenticated.
        """
        request = self.factory.get(f"/events/{self.event.slug}/")
        request.resolver_match = MagicMock(
            kwargs={
                "event_slug": self.event.slug,
            },
        )
        request.user = MagicMock(is_authenticated=False)

        context = event_context(request)

        self.assertEqual(context["event"], self.event)
        self.assertFalse(context["can_edit_event"])

    def test_event_context_user_can_edit_event(self):
        """
        Test that 'can_edit_event' is True if the user is the event author.
        """
        request = self.factory.get(f"/events/{self.event.slug}/")
        request.resolver_match = MagicMock(
            kwargs={
                "event_slug": self.event.slug,
            },
        )
        request.user = self.user

        with patch(
            "kns.events.models.Event.can_edit_event",
            return_value=True,
        ):
            context = event_context(request)

        self.assertEqual(context["event"], self.event)
        self.assertTrue(context["can_edit_event"])

    def test_event_context_user_cannot_edit_event(self):
        """
        Test that 'can_edit_event' is False if the user is not the event author.
        """
        # Create another user who is not the author
        another_user = User.objects.create_user(
            email="anotheruser@example.com",
            password="password123",
        )

        request = self.factory.get(f"/events/{self.event.slug}/")
        request.resolver_match = MagicMock(
            kwargs={
                "event_slug": self.event.slug,
            },
        )
        request.user = another_user

        with patch(
            "kns.events.models.Event.can_edit_event",
            return_value=False,
        ):
            context = event_context(request)

        self.assertEqual(context["event"], self.event)
        self.assertFalse(context["can_edit_event"])
