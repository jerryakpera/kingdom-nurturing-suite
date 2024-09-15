from django import forms
from django.conf import settings
from django.test import TestCase

from kns.core.models import Setting
from kns.custom_user.models import User
from kns.mentorships.models import MentorshipArea

from ..forms import ProfileMentorshipAreasForm


class ProfileMentorshipAreasFormTests(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        Creates sample MentorshipArea objects and settings.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        self.area1 = MentorshipArea.objects.create(
            title="Software Engineering",
            content="Mentorship on software engineering",
            author=self.profile,
            status="published",
        )
        self.area2 = MentorshipArea.objects.create(
            title="Data Science",
            content="Mentorship on data science",
            author=self.profile,
            status="published",
        )

        self.setting = Setting.objects.create(
            max_mentorship_areas_per_user=3,
        )

    def test_form_fields(self):
        """
        Test that the form has the correct fields and attributes.
        """
        form = ProfileMentorshipAreasForm()

        # Check fields
        self.assertIn("mentorship_areas", form.fields)

        # Check field types
        self.assertIsInstance(
            form.fields["mentorship_areas"],
            forms.ModelMultipleChoiceField,
        )

        # Check widget attributes
        self.assertEqual(
            form.fields["mentorship_areas"].widget.attrs["id"],
            "mentorship_areas",
        )
        self.assertIn(
            "class",
            form.fields["mentorship_areas"].widget.attrs,
        )

    def test_form_validation(self):
        """
        Test that the form validates correctly with valid data.
        """
        data = {
            "mentorship_areas": [
                self.area1.id,
                self.area2.id,
            ],
        }

        form = ProfileMentorshipAreasForm(data=data)

        self.assertTrue(form.is_valid())

    def test_form_too_many_areas(self):
        """
        Test that the form raises an error if too many mentorship
        areas are selected.
        """
        area3 = MentorshipArea.objects.create(
            title="Project Management",
            content="Mentorship on project management",
            author=self.profile,
            status="published",
        )

        data = {
            "mentorship_areas": [
                self.area1.id,
                self.area2.id,
                area3.id,
            ],
        }

        self.setting.max_mentorship_areas_per_user = 2
        self.setting.save()

        form = ProfileMentorshipAreasForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("mentorship_areas", form.errors)

        self.assertEqual(
            form.errors["mentorship_areas"],
            [
                (
                    "You can select up to "
                    f"{self.setting.max_mentorship_areas_per_user} mentorship areas."
                )
            ],
        )

    def test_form_invalid_data(self):
        """
        Test that the form handles invalid data correctly.
        """
        data = {
            "mentorship_areas": [],
        }
        form = ProfileMentorshipAreasForm(data=data)

        self.assertFalse(form.is_valid())

    def test_form_initial_data(self):
        """
        Test that the form is initialized with the correct data.
        """
        form = ProfileMentorshipAreasForm()
        expected_queryset = list(MentorshipArea.objects.filter(status="published"))

        self.assertQuerySetEqual(
            list(form.fields["mentorship_areas"].queryset),
            expected_queryset,
            ordered=False,  # Allow unordered comparison
        )
