from kns.custom_user.models import User
from kns.profiles.models import Profile


class ProfileModelTests:
    def setUp(self):
        # Set up any necessary data for the tests
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
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

    def test_profile_created_at_exists(self):
        """
        Test that the created_at field exists on the profile instance.
        """

        profile = Profile.objects.get(user=self.user)

        assert profile.created_at is not None

    def test_profile_updated_at_exists(self):
        """
        Test that the updated_at field exists on the profile instance.
        """

        profile = Profile.objects.get(user=self.user)

        assert profile.updated_at is not None

    def test_profile_verified_exists(self):
        """
        Test that the verified field exists on the profile instance.
        """

        profile = Profile.objects.get(user=self.user)

        assert profile.verified is not None
        assert not profile.verified

    def test_profile_is_visitor_exists(self):
        """
        Test that the is_visitor field exists on the profile instance.
        """

        profile = Profile.objects.get(user=self.user)

        assert profile.is_visitor is not None
        assert not profile.is_visitor

    def test_profile_agreed_to_terms_exists(self):
        """
        Test that the agreed_to_terms field exists on the profile instance.
        """

        profile = Profile.objects.get(user=self.user)

        assert profile.agreed_to_terms is not None
        assert not profile.agreed_to_terms
