from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from kns.custom_user.models import User

from ..models import Event
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

    def test_duration_no_end_date(self):
        """
        Test the `duration` property when there is no end date set.
        """
        # Set a start date for the event
        self.event.start_date = timezone.now().date()
        self.event.end_date = None  # No end date
        self.event.save()

        # Assert that the duration is 0 when there is no end date
        self.assertEqual(self.event.duration, 0)

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

    def test_slug_generation_on_save(self):
        """
        Test that a slug is generated from the title when saving the event.
        """
        event = Event(
            title="Test Event",
            author=self.profile,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=1),
            registration_deadline_date=timezone.now().date() + timedelta(days=2),
        )

        event.save()

        # Check that the slug was generated correctly
        self.assertEqual(event.slug, slugify(event.title))  # This should now pass

    def test_slug_uniqueness(self):
        """
        Test that slug uniqueness is enforced when saving multiple events with the same title.
        """
        # Create the first event with the required fields
        Event.objects.create(
            title="Unique Title",
            author=self.profile,
            start_date=timezone.now().date(),  # Set a valid start date
            end_date=timezone.now().date() + timedelta(days=1),  # Set a valid end date
            registration_deadline_date=timezone.now().date() + timedelta(days=2),
        )

        # Attempt to create a second event with the same title
        event_with_duplicate_slug = Event(
            title="Unique Title",
            author=self.profile,
            start_date=timezone.now().date(),  # Set a valid start date
            end_date=timezone.now().date() + timedelta(days=1),  # Set a valid end date
            registration_deadline_date=timezone.now().date() + timedelta(days=2),
        )

        # This should raise a ValidationError due to the slug uniqueness constraint
        with self.assertRaises(ValidationError):
            event_with_duplicate_slug.full_clean()  # Validate the instance

    def test_end_date_validation(self):
        """
        Test that a ValidationError is raised if the end date is earlier than the start date.
        """
        event = Event(
            title="Event with Invalid Dates",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() - timedelta(days=1),
            author=self.profile,
        )

        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_event_duration(self):
        """
        Test that the duration property calculates the correct number of days.
        """
        self.event.start_date = timezone.now().date()
        self.event.end_date = self.event.start_date + timedelta(days=3)
        self.event.save()

        self.assertEqual(self.event.duration, 3)

    def test_event_is_upcoming(self):
        """
        Test that the is_upcoming method correctly identifies an upcoming event.
        """
        self.event.start_date = timezone.now().date() + timedelta(days=5)
        self.assertTrue(self.event.is_upcoming())

        self.event.start_date = timezone.now().date() - timedelta(days=2)
        self.assertFalse(self.event.is_upcoming())

    def test_get_absolute_url(self):
        """
        Test the get_absolute_url method to ensure it returns
        the correct URL for the event detail page.
        """
        expected_url = reverse(
            "events:event_detail",
            kwargs={
                "event_slug": self.event.slug,
            },
        )

        self.assertEqual(self.event.get_absolute_url(), expected_url)
