from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.events.models import Event

from . import test_constants


class TestIndexView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user
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

        # Create a sample event
        self.event = Event.objects.create(
            title="Test Event",
            summary="This is a test event.",
            description="Detailed description of the test event.",
            start_date="2024-01-01",
            end_date="2024-01-02",
            location_country="NG",
            location_city="Lagos",
            author=self.user.profile,
        )

    def test_index_view(self):
        """
        Test the index view to ensure it renders the list of events.
        """
        url = reverse("events:index")
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "events/pages/index.html",
        )

        # Ensure the created event is present in the context
        self.assertIn(self.event, response.context["events"])


class TestEventDetailView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user and log in
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

        self.event = Event.objects.create(
            title=test_constants.EVENT_TITLE,
            summary=test_constants.EVENT_SUMMARY,
            description=test_constants.EVENT_DESCRIPTION,
            start_date=test_constants.VALID_START_DATE,
            end_date=test_constants.VALID_END_DATE,
            location_country=test_constants.VALID_COUNTRY,
            location_city=test_constants.VALID_CITY,
            author=self.user.profile,
        )

    def test_event_detail_view(self):
        """
        Test the event detail view to ensure it renders the specific event.
        """

        url = reverse(
            "events:event_detail",
            kwargs={
                "event_slug": self.event.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "events/pages/event_detail.html",
        )

        # Ensure the event details are present
        self.assertIn(
            self.event.title,
            response.content.decode(),
        )

        self.assertIn(
            self.event.summary,
            response.content.decode(),
        )


class TestEventActivitiesView(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user and log in
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

        # Create a sample event
        self.event = Event.objects.create(
            title="Test Event",
            summary="This is a test event.",
            description="Detailed description of the test event.",
            start_date="2024-01-01",
            end_date="2024-01-02",
            location_country="NG",
            location_city="Lagos",
            author=self.user.profile,
        )

    def test_event_activities_view(self):
        """
        Test the event activities view to ensure it renders the activities
        page for a specific event.
        """
        url = reverse(
            "events:event_activities",
            kwargs={
                "event_slug": self.event.slug,
            },
        )
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(
            response,
            "events/pages/event_activities.html",
        )

        # Ensure the event details are present in the response
        self.assertIn(
            self.event.title,
            response.content.decode(),
        )

        self.assertIn(
            self.event.summary,
            response.content.decode(),
        )
