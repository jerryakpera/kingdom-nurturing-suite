"""
Tests for the forms in the `events` app.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .. import constants as event_constants
from ..forms import (
    EventContactForm,
    EventContentForm,
    EventDatesForm,
    EventLocationForm,
    EventMiscForm,
)
from .test_constants import VALID_REGISTRATION_LIMIT


class TestEventContentForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        self.form_data = {
            "title": "Exciting Event Title",
            "summary": (
                "This is a brief summary of the exciting event that spans multiple days. "
                "It contains enough details to meet the minimum length requirement "
                "for a valid event summary."
            ),
            "description": (
                "This is a detailed description of the exciting event "
                "with all necessary information."
            ),
            "tags": "exciting,event,fun",
        }

    def test_event_content_form_valid(self):
        """
        Test if the form is valid when correct data is provided.
        """
        form = EventContentForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_event_title_too_short(self):
        """
        Test that a title shorter than the minimum length is invalid.
        """
        self.form_data["title"] = "Short"

        form = EventContentForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertEqual(
            form.errors["title"],
            [
                "The title must be at least "
                f"{event_constants.EVENT_TITLE_MIN_LENGTH} characters long"
            ],
        )

    def test_event_title_too_long(self):
        """
        Test that a title longer than the maximum length is invalid.
        """
        self.form_data["title"] = "A" * (event_constants.EVENT_TITLE_MAX_LENGTH + 1)

        form = EventContentForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertEqual(
            form.errors["title"],
            [
                "The title must be at most "
                f"{event_constants.EVENT_TITLE_MAX_LENGTH} characters long"
            ],
        )

    def test_event_summary_too_short(self):
        """
        Test that a summary shorter than the minimum length is invalid.
        """

        self.form_data["summary"] = "Too short"

        form = EventContentForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("summary", form.errors)
        self.assertEqual(
            form.errors["summary"],
            [
                (
                    "The event summary must be at least "
                    f"{event_constants.EVENT_SUMMARY_MIN_LENGTH} characters long"
                )
            ],
        )

    def test_event_summary_too_long(self):
        """
        Test that a summary longer than the maximum length is invalid.
        """

        self.form_data["summary"] = "A" * (event_constants.EVENT_SUMMARY_MAX_LENGTH + 1)

        form = EventContentForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("summary", form.errors)
        self.assertEqual(
            form.errors["summary"],
            [
                (
                    "The event summary must be no more than "
                    f"{event_constants.EVENT_SUMMARY_MAX_LENGTH} characters long"
                )
            ],
        )

    def test_event_tags_too_many(self):
        """
        Test that more than 5 tags are not allowed.
        """

        self.form_data["tags"] = "tag1,tag2,tag3,tag4,tag5,tag6"

        form = EventContentForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("tags", form.errors)
        self.assertEqual(
            form.errors["tags"],
            [
                f"An event cannot have more than {event_constants.MAX_TAGS} tags.",
            ],
        )

    def test_event_form_without_tags(self):
        """
        Test that the form is valid even if tags are not provided.
        """

        self.form_data.pop("tags")

        form = EventContentForm(data=self.form_data)

        self.assertTrue(form.is_valid())


class TestEventDatesForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """

        self.valid_start_date = timezone.now().date() + timedelta(
            days=event_constants.EVENT_MIN_DAYS_IN_FUTURE + 1
        )
        self.valid_end_date = self.valid_start_date + timedelta(days=1)
        self.valid_registration_deadline = self.valid_start_date - timedelta(days=1)

        self.form_data = {
            "start_date": self.valid_start_date,
            "end_date": self.valid_end_date,
            "registration_deadline_date": self.valid_registration_deadline,
        }

    def test_event_dates_form_valid(self):
        """
        Test if the form is valid when correct data is provided.
        """

        form = EventDatesForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_start_date_too_soon(self):
        """
        Test that a start date less than the minimum required days in the future is invalid.
        """
        self.form_data["start_date"] = timezone.now().date() + timedelta(
            days=event_constants.EVENT_MIN_DAYS_IN_FUTURE - 1
        )

        form = EventDatesForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("start_date", form.errors)
        self.assertEqual(
            form.errors["start_date"],
            [event_constants.ERROR_START_DATE_FUTURE],
        )

    def test_end_date_before_start_date(self):
        """
        Test that an end date before the start date is invalid.
        """
        self.form_data["end_date"] = self.valid_start_date - timedelta(days=1)

        form = EventDatesForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)
        self.assertEqual(
            form.errors["end_date"],
            [event_constants.ERROR_END_DATE],
        )

    def test_registration_deadline_after_start_date(self):
        """
        Test that a registration deadline that is not before the event start date is invalid.
        """
        self.form_data["registration_deadline_date"] = self.valid_start_date

        form = EventDatesForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("registration_deadline_date", form.errors)
        self.assertEqual(
            form.errors["registration_deadline_date"],
            [event_constants.ERROR_REGISTRATION_DEADLINE],
        )

    def test_registration_deadline_before_start_date(self):
        """
        Test that a valid registration deadline before the start date is valid.
        """
        self.form_data["registration_deadline_date"] = (
            self.valid_start_date - timedelta(days=1)
        )

        form = EventDatesForm(data=self.form_data)

        self.assertTrue(form.is_valid())


class TestEventLocationForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        self.form_data = {
            "location_country": "US",
            "location_city": "New York",
        }

    def test_event_location_form_valid(self):
        """
        Test if the form is valid when correct data is provided.
        """
        form = EventLocationForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_country_field_required(self):
        """
        Test that the country field is required.
        """
        self.form_data["location_country"] = ""
        self.form_data["location_city"] = ""

        form = EventLocationForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("location_country", form.errors)
        self.assertEqual(
            form.errors["location_country"],
            [
                "This field is required.",
                event_constants.ERROR_NO_COUNTRY_AND_CITY,
            ],
        )

    def test_city_field_required(self):
        """
        Test that the city field is required.
        """
        self.form_data["location_city"] = ""

        form = EventLocationForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("location_city", form.errors)
        self.assertEqual(
            form.errors["location_city"],
            [
                "This field is required.",
                event_constants.ERROR_NO_LOCATION_CITY,
            ],
        )

    def test_city_without_country(self):
        """
        Test that the city field cannot be filled without a country.
        """
        self.form_data["location_city"] = "Los Angeles"
        self.form_data["location_country"] = ""

        form = EventLocationForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("location_country", form.errors)
        self.assertEqual(
            form.errors["location_country"],
            [
                "This field is required.",
                event_constants.ERROR_NO_LOCATION_COUNTRY,
            ],
        )

    def test_country_without_city(self):
        """
        Test that the country field cannot be filled without a city.
        """
        self.form_data["location_country"] = "US"
        self.form_data["location_city"] = ""

        form = EventLocationForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("location_city", form.errors)
        self.assertEqual(
            form.errors["location_city"],
            [
                "This field is required.",
                event_constants.ERROR_NO_LOCATION_CITY,
            ],
        )


class TestEventMiscForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        # Define event dates
        self.start_date = timezone.now().date() + timedelta(days=1)
        self.end_date = self.start_date + timedelta(days=1)

        # Define form data
        self.form_data = {
            "refreshments": True,
            "accommodation": True,
            "registration_limit": VALID_REGISTRATION_LIMIT,
        }

    def test_event_misc_form_valid(self):
        """
        Test if the form is valid when correct data is provided.
        """
        form = EventMiscForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_registration_limit_required(self):
        """
        Test that the registration limit is required.
        """
        self.form_data["registration_limit"] = None

        form = EventMiscForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn(
            "registration_limit",
            form.errors,
        )

        self.assertEqual(
            form.errors["registration_limit"],
            ["This field is required."],
        )

    def test_registration_limit_too_low(self):
        """
        Test that a registration limit less than 1 is invalid.
        """
        # Test for zero
        self.form_data["registration_limit"] = 0

        form = EventMiscForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("registration_limit", form.errors)
        self.assertEqual(
            form.errors["registration_limit"][0],
            event_constants.REGISTRATION_LIMIT_ERROR_MESSAGE,
        )


class TestEventContactForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        self.form_data = {
            "event_contact_name": "John Doe",
            "event_contact_email": "john.doe@example.com",
        }

    def test_event_contact_form_valid(self):
        """
        Test if the form is valid when correct data is provided.
        """
        form = EventContactForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_event_contact_name_required(self):
        """
        Test that the contact name is required.
        """
        self.form_data["event_contact_name"] = ""

        form = EventContactForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("event_contact_name", form.errors)
        self.assertEqual(
            form.errors["event_contact_name"],
            [event_constants.ERROR_CONTACT_NAME_REQUIRED],
        )

    def test_event_contact_email_required(self):
        """
        Test that the email field is required.
        """
        self.form_data["event_contact_email"] = ""

        form = EventContactForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("event_contact_email", form.errors)
        self.assertEqual(
            form.errors["event_contact_email"],
            [
                event_constants.ERROR_CONTACT_EMAIL_REQUIRED,
            ],
        )

    def test_event_contact_email_invalid_format(self):
        """
        Test that an invalid email format is considered invalid.
        """
        self.form_data["event_contact_email"] = "not-an-email"

        form = EventContactForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("event_contact_email", form.errors)
        self.assertEqual(
            form.errors["event_contact_email"],
            ["Enter a valid email address."],
        )
