from django.test import TestCase

from kns.custom_user.models import User
from kns.profiles.forms import ProfileSettingsForm


class TestProfileSettingsForm(TestCase):
    def setUp(self):
        """
        Create a user and associated profile for testing.
        """

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

    def test_profile_settings_form_initial(self):
        """
        Test the initial state of the ProfileSettingsForm.
        """
        form = ProfileSettingsForm(instance=self.profile)

        # Ensure that fields are not required by default
        self.assertFalse(
            form.fields["bio_details_is_visible"].required,
        )
        self.assertFalse(
            form.fields["contact_details_is_visible"].required,
        )

    def test_profile_settings_form_valid_data(self):
        """
        Test the ProfileSettingsForm with valid data.
        """
        form_data = {
            "bio_details_is_visible": True,
            "contact_details_is_visible": False,
        }
        form = ProfileSettingsForm(
            data=form_data,
            instance=self.profile,
        )
        self.assertTrue(form.is_valid())

        # Save the form and check the changes
        form.save()
        self.profile.refresh_from_db()

        self.assertTrue(self.profile.bio_details_is_visible)
        self.assertFalse(self.profile.contact_details_is_visible)
