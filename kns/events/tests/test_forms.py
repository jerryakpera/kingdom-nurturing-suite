"""
Tests for the forms in the `events` app.
"""

from django.test import TestCase

from kns.core.utils import log_this

from .. import constants as event_constants
from ..forms import EventContentForm


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

        log_this(form.errors)

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
