from django.test import TestCase

from kns.custom_user.models import User
from kns.profiles.models import Profile


class ProfileModelTests(TestCase):
    def setUp(self):
        # Set up any necessary data for the tests
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

    def test_profile_creation_on_user_creation(self):
        """
        Test that a Profile instance is created when a User instance is created.
        """
        # Fetch the profile associated with the user
        profile = Profile.objects.get(user=self.user)

        # Check that the profile exists and has the correct email
        self.assertIsNotNone(profile)
        self.assertEqual(profile.email, self.user.email)

    def test_profile_email_unique_constraint(self):
        """
        Test that the email field on the Profile model is unique.
        """
        # Create a user with a specific email
        User.objects.create_user(
            email="uniqueuser@example.com", password="testpassword"
        )

        # Create a second user with the same email
        with self.assertRaises(Exception) as context:
            User.objects.create_user(
                email="uniqueuser@example.com", password="anotherpassword"
            )

        # Check if the exception is related to the unique constraint
        self.assertTrue("UNIQUE constraint failed" in str(context.exception))
