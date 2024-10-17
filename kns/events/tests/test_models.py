from datetime import datetime, timedelta

from django.test import Client, TestCase
from django.utils import timezone
from django.utils.text import slugify

from kns.custom_user.models import User

from .factories import EventFactory


class TestEventFactory(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
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

    def test_factory(self):
        """
        The factory produces a valid instance of Event.
        """
        event = EventFactory()

        self.assertIsNotNone(event)
        self.assertNotEqual(event.title, "")
        self.assertNotEqual(event.description, "")
        self.assertIsNotNone(event.author)
        self.assertIsNotNone(event.start_date)
        self.assertIsNotNone(event.event_contact_email)

    def test_slug_generation(self):
        """
        Test if slug is generated correctly based on title.
        """
        event = EventFactory(title="Sample Event Title")
        self.assertEqual(event.slug, slugify("Sample Event Title"))

    def test_str_method(self):
        """
        Return the correct string representation of the event.
        """
        event = EventFactory(
            title="Community Gathering",
            start_date=datetime.strptime(
                "2024-10-20", "%Y-%m-%d"
            ),  # Convert string to datetime
        )

        self.assertEqual(
            str(event), "Community Gathering"
        )  # Update this based on your __str__ implementation


class TestEvent(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating necessary objects.
        """
        # Create a profile to act as the event author
        self.user = User.objects.create_user(
            email="organizer@example.com",
            password="password123",
        )
        self.profile = self.user.profile

        # Create an event instance using the factory
        self.event = EventFactory(author=self.profile)

    def test_str_method(self):
        """
        Test the __str__ method to ensure it returns the event title.
        """
        event = EventFactory(title="Sample Event")

        self.assertEqual(str(event), "Sample Event")

    def test_duration(self):
        """
        Test the `duration` property to ensure it returns the correct number of days.
        """
        self.event.start_date = timezone.now().date()
        self.event.end_date = self.event.start_date + timedelta(days=2)
        self.event.save()

        self.assertEqual(self.event.duration, 2)

    def test_location_display(self):
        """
        Test the `location_display` method to ensure it returns the correct location string.
        """
        self.event.location_country = "KE"
        self.event.location_city = "Nairobi"
        self.assertEqual(
            self.event.location_display(),
            "Kenya, Nairobi",
        )

        self.event.location_city = ""
        self.assertEqual(self.event.location_display(), "Kenya")

        self.event.location_country = None
        self.assertEqual(self.event.location_display(), "None")

    def test_days_until_event(self):
        """
        Test the `days_until_event` method to ensure it returns the correct number of days left.
        """
        self.event.start_date = timezone.now().date() + timedelta(days=5)
        self.event.save()

        self.assertEqual(self.event.days_until_event(), 5)

        # Past event
        self.event.start_date = timezone.now().date() - timedelta(days=3)
        self.event.save()

        self.assertEqual(self.event.days_until_event(), 0)

    def test_has_registration_deadline_passed(self):
        """
        Test the `has_registration_deadline_passed` method to ensure it returns the correct result.
        """
        self.event.registration_deadline_date = timezone.now().date() - timedelta(
            days=1
        )
        self.assertTrue(self.event.has_registration_deadline_passed())

        self.event.registration_deadline_date = timezone.now().date() + timedelta(
            days=1
        )
        self.assertFalse(self.event.has_registration_deadline_passed())

    def test_is_upcoming(self):
        """
        Test the `is_upcoming` method to ensure it correctly identifies upcoming events.
        """
        self.event.start_date = timezone.now().date() + timedelta(days=2)
        self.assertTrue(self.event.is_upcoming())

        self.event.start_date = timezone.now().date() - timedelta(days=1)
        self.assertFalse(self.event.is_upcoming())
