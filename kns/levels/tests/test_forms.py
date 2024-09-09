from django import forms
from django.conf import settings
from django.test import TestCase

from kns.custom_user.models import User

from ..forms import ProfileLevelForm
from ..models import Level, Sublevel


class ProfileLevelFormTests(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        Creates sample Level and Sublevel objects.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        self.level1 = Level.objects.create(
            title="Level 1",
            content="Content for level 1",
            author=self.profile,
        )
        self.level2 = Level.objects.create(
            title="Level 2",
            content="Content for level 2",
            author=self.profile,
        )
        self.sublevel1 = Sublevel.objects.create(
            title="Sublevel 1",
            content="Content for sublevel 1",
            author=self.profile,
        )
        self.sublevel2 = Sublevel.objects.create(
            title="Sublevel 2",
            content="Content for sublevel 2",
            author=self.profile,
        )

    def test_form_fields(self):
        """
        Test that the form has the correct fields and attributes.
        """
        form = ProfileLevelForm()

        # Check fields
        self.assertIn("level", form.fields)
        self.assertIn("sublevel", form.fields)
        self.assertIn("url", form.fields)

        # Check field types
        self.assertIsInstance(
            form.fields["level"],
            forms.ModelChoiceField,
        )
        self.assertIsInstance(
            form.fields["sublevel"],
            forms.ModelChoiceField,
        )
        self.assertIsInstance(
            form.fields["url"],
            forms.CharField,
        )

        # Check widgets
        self.assertEqual(
            form.fields["level"].widget.attrs["id"],
            "level_select",
        )
        self.assertEqual(
            form.fields["sublevel"].widget.attrs["id"],
            "sublevel_select",
        )
        self.assertEqual(
            form.fields["url"].widget.attrs["id"],
            "url_input",
        )

    def test_form_initial_data(self):
        """
        Test that the form is initialized with the correct data.
        """
        form = ProfileLevelForm()
        self.assertEqual(
            form.fields["url"].widget.attrs["data-url"],
            settings.API_URL,
        )

    def test_form_validation(self):
        """
        Test that the form validates correctly with valid data.
        """
        data = {
            "level": self.level1.id,
            "sublevel": self.sublevel1.id,
            "url": settings.API_URL,
        }
        form = ProfileLevelForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        """
        Test that the form handles invalid data correctly.
        """
        data = {
            "level": "",
            "sublevel": self.sublevel1.id,
            "url": settings.API_URL,
        }
        form = ProfileLevelForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("level", form.errors)

    def test_form_disabled_sublevel_field(self):
        """
        Test that the sublevel field is disabled by default.
        """
        form = ProfileLevelForm()
        self.assertTrue(form.fields["sublevel"].widget.attrs["disabled"])
