from django.test import Client, TestCase
from django.urls import reverse

from kns.custom_user.models import User
from kns.profiles.models import Profile
from kns.vocations.models import ProfileVocation, Vocation


class TestVocationModel(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a user and a profile
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"

        self.profile.save()

        # Create a vocation
        self.vocation = Vocation.objects.create(
            title="Software Developer",
            description="Builds and maintains software systems.",
            author=self.profile,
        )

    def test_vocation_creation(self):
        """
        Test that the Vocation instance is created successfully and the fields are populated.
        """
        self.assertIsNotNone(self.vocation)
        self.assertEqual(self.vocation.title, "Software Developer")

        self.assertEqual(
            self.vocation.description, "Builds and maintains software systems."
        )
        self.assertEqual(self.vocation.author, self.profile)

    def test_str_method(self):
        """
        Test that the __str__ method returns the correct string representation.
        """
        self.assertEqual(str(self.vocation), "Software Developer")

    def test_vocation_repr(self):
        """
        Test the __repr__ method for proper debugging output.
        """
        expected_repr = (
            f"<Vocation(title=Software Developer, author={self.profile.user.username})>"
        )

        self.assertEqual(repr(self.vocation), expected_repr)

    def test_get_absolute_url(self):
        """
        Test the get_absolute_url method to ensure it returns the correct URL.
        """
        expected_url = reverse(
            "vocations:vocation_detail",
            kwargs={
                "vocation_id": self.vocation.id,
            },
        )
        self.assertEqual(
            self.vocation.get_absolute_url(),
            expected_url,
        )


class TestProfileVocationModel(TestCase):
    def setUp(self):
        self.client = Client()

        # Create two users and their profiles
        self.user1 = User.objects.create_user(
            email="testuser1@example.com",
            password="password1",
        )
        self.profile1 = self.user1.profile
        self.profile1.first_name = "Alice"
        self.profile1.last_name = "Wonder"
        self.profile1.save()

        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="password2",
        )
        self.profile2 = self.user2.profile
        self.profile2.first_name = "Bob"
        self.profile2.last_name = "Builder"
        self.profile2.save()

        # Create a vocation
        self.vocation = Vocation.objects.create(
            title="Carpenter",
            description="Works with wood to build structures.",
            author=self.profile1,
        )

        # Assign the vocation to the profile
        self.profile_vocation = ProfileVocation.objects.create(
            profile=self.profile2,
            vocation=self.vocation,
        )

    def test_profile_vocation_creation(self):
        """
        Test that ProfileVocation instance is created successfully.
        """
        self.assertIsNotNone(self.profile_vocation)
        self.assertEqual(self.profile_vocation.profile, self.profile2)
        self.assertEqual(self.profile_vocation.vocation, self.vocation)

    def test_unique_together_constraint(self):
        """
        Test the unique_together constraint for ProfileVocation.
        """
        with self.assertRaises(Exception):
            # Try to create a duplicate entry
            ProfileVocation.objects.create(
                profile=self.profile2,
                vocation=self.vocation,
            )

    def test_str_method(self):
        """
        Test the __str__ method for ProfileVocation.
        """
        expected_str = f"{self.profile2.get_full_name()} - {self.vocation.title}"
        self.assertEqual(str(self.profile_vocation), expected_str)
