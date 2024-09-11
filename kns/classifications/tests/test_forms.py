from django import forms
from django.conf import settings
from django.test import TestCase

from kns.custom_user.models import User

from ..forms import ProfileClassificationForm
from ..models import Classification, Subclassification


class ProfileClassificationFormTests(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        Creates sample Classification and Subclassification objects.
        """
        self.user = User.objects.create_user(
            email="jane.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()

        self.classification1 = Classification.objects.create(
            title="Classification 1",
            content="Content for classification 1",
            author=self.profile,
            order=1,
        )
        self.classification2 = Classification.objects.create(
            title="Classification 2",
            content="Content for classification 2",
            author=self.profile,
            order=2,
        )
        self.subclassification1 = Subclassification.objects.create(
            title="Subclassification 1",
            content="Content for subclassification 1",
            author=self.profile,
        )
        self.subclassification2 = Subclassification.objects.create(
            title="Subclassification 2",
            content="Content for subclassification 2",
            author=self.profile,
        )

    def test_form_fields(self):
        """
        Test that the form has the correct fields and attributes.
        """
        form = ProfileClassificationForm()

        # Check fields
        self.assertIn("classification", form.fields)
        self.assertIn("subclassification", form.fields)
        self.assertIn("url", form.fields)

        # Check field types
        self.assertIsInstance(
            form.fields["classification"],
            forms.ModelChoiceField,
        )
        self.assertIsInstance(
            form.fields["subclassification"],
            forms.ModelChoiceField,
        )
        self.assertIsInstance(
            form.fields["url"],
            forms.CharField,
        )

        # Check widgets
        self.assertEqual(
            form.fields["classification"].widget.attrs["id"],
            "classification_select",
        )
        self.assertEqual(
            form.fields["subclassification"].widget.attrs["id"],
            "subclassification_select",
        )
        self.assertEqual(
            form.fields["url"].widget.attrs["id"],
            "url_input",
        )

    def test_form_initial_data(self):
        """
        Test that the form is initialized with the correct data.
        """
        form = ProfileClassificationForm()
        self.assertEqual(
            form.fields["url"].widget.attrs["data-url"],
            settings.API_URL,
        )

    def test_form_validation(self):
        """
        Test that the form validates correctly with valid data.
        """
        data = {
            "classification": self.classification1.id,
            "subclassification": self.subclassification1.id,
            "url": settings.API_URL,
        }
        form = ProfileClassificationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        """
        Test that the form handles invalid data correctly.
        """
        data = {
            "classification": "",  # Invalid classification
            "subclassification": self.subclassification1.id,
            "url": settings.API_URL,
        }
        form = ProfileClassificationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("classification", form.errors)

    def test_form_disabled_subclassification_field(self):
        """
        Test that the subclassification field is disabled by default.
        """
        form = ProfileClassificationForm()
        self.assertTrue(
            form.fields["subclassification"].widget.attrs["disabled"],
        )
