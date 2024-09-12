import pytest
from django.db import IntegrityError
from django.test import TestCase

from kns.custom_user.models import User
from kns.mentorships.models import MentorshipArea


class TestMentorshipAreaModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """
        self.user = User.objects.create_user(
            email="jane.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Jane"
        self.profile.last_name = "Doe"

        self.profile.save()

    def test_mentorship_area_creation(self):
        """
        Test that a MentorshipArea instance can be created and is properly saved.
        """
        mentorship_area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="<p>Advanced concepts in software development.</p>",
            author=self.profile,
        )

        self.assertEqual(mentorship_area.title, "Software Engineering")
        self.assertEqual(
            mentorship_area.content, "<p>Advanced concepts in software development.</p>"
        )

    def test_mentorship_area_slug_unique(self):
        """
        Test that the slug field on the MentorshipArea model is unique.
        """
        MentorshipArea.objects.create(
            title="Software Engineering",
            content="<p>Advanced concepts in software development.</p>",
            author=self.profile,
        )

        with pytest.raises(IntegrityError) as excinfo:
            MentorshipArea.objects.create(
                title="Software Engineering",
                content="<p>Different content.</p>",
                author=self.profile,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_mentorship_area_str_method(self):
        """
        Test that the __str__ method returns the title of the mentorship area.
        """
        mentorship_area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="<p>Advanced concepts in software development.</p>",
            author=self.profile,
        )

        self.assertEqual(str(mentorship_area), "Software Engineering")
