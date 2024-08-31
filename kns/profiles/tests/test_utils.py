from datetime import timedelta
from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.utils import timezone

from kns.custom_user.models import User
from kns.groups.models import Group, GroupMember
from kns.profiles.db_data import encryption_reasons
from kns.profiles.models import EncryptionReason, Profile
from kns.profiles.utils import (
    calculate_max_dob,
    get_profile_slug,
    is_profiles_group_leader,
    name_with_apostrophe,
    populate_encryption_reasons,
)


class TestGetProfileSlug(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("django.urls.resolve")
    def test_get_profile_slug_with_valid_slug(self, mock_resolve):
        """
        Test if a valid profile slug is extracted correctly from the URL path.
        """
        # Mock the resolve function to return a match with profile_slug
        mock_resolve.return_value.kwargs = {"profile_slug": "test-slug"}

        request = self.factory.get("/profiles/test-slug/")
        request.path_info = "/profiles/test-slug/"

        slug = get_profile_slug(request)

        self.assertEqual(slug, "test-slug")

    @patch("django.urls.resolve")
    def test_get_profile_slug_with_non_profiles_path(self, mock_resolve):
        """
        Test if no slug is extracted when the path does not start with /profiles/.
        """
        # Mock the resolve function, though it shouldn't be called in this case
        mock_resolve.return_value.kwargs = {}

        request = self.factory.get("/some/other/path/")
        request.path_info = "/some/other/path/"

        slug = get_profile_slug(request)

        self.assertEqual(slug, "")

    @patch("django.urls.resolve")
    def test_get_profile_slug_with_no_slug(self, mock_resolve):
        """
        Test if no slug is extracted when the path is correct but no slug is present.
        """
        # Mock the resolve function to return an empty kwargs
        mock_resolve.return_value.kwargs = {}

        request = self.factory.get("/profiles/")
        request.path_info = "/profiles/"

        slug = get_profile_slug(request)

        self.assertEqual(slug, "")


class TestCalculateMaxDob(TestCase):
    def test_calculate_max_dob(self):
        """
        Test that calculate_max_dob returns the correct date for a given age.
        """
        # Assume today's date is 2024-08-29
        age = 30
        expected_max_dob = (
            timezone.now().date() - timedelta(days=(age * 365))
        ).strftime("%Y-%m-%d")
        self.assertEqual(calculate_max_dob(age), expected_max_dob)


class TestNameWithApostrophe(TestCase):
    def test_name_with_apostrophe_ends_with_s(self):
        """
        Test that name_with_apostrophe adds just an apostrophe if the name ends with 's'.
        """
        name = "James"
        result = name_with_apostrophe(name)
        self.assertEqual(result, "James'")

    def test_name_with_apostrophe_does_not_end_with_s(self):
        """
        Test that name_with_apostrophe adds 's if the name does not end with 's'.
        """
        name = "John"
        result = name_with_apostrophe(name)
        self.assertEqual(result, "John's")


class PopulateSkillsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )

        self.profile = self.user.profile

        # Modify encryption_reasons for testing if necessary
        self.encryption_reasons = encryption_reasons

    def test_encryption_reasons_are_created_correctly(self):
        # Override the encryption reasons in the module with test data

        # Call the function
        populate_encryption_reasons(self.encryption_reasons)

        # Check that the correct number of encryption reasons were created
        self.assertEqual(EncryptionReason.objects.count(), len(self.encryption_reasons))

        # Check that each encryption_reason was created with the correct data
        for i, encryption_reason_data in enumerate(self.encryption_reasons):
            encryption_reason = EncryptionReason.objects.get(
                title=encryption_reason_data["title"]
            )
            self.assertEqual(
                encryption_reason.description,
                encryption_reason_data["description"],
            )
            self.assertEqual(encryption_reason.author, self.profile)

    def test_no_encryption_reasons_created_if_no_predefined_encryption_reasons(self):
        # Override the encryption reasons in the module with an empty list
        self.encryption_reasons = []

        # Call the function
        populate_encryption_reasons(self.encryption_reasons)

        # Check that no encryption reasons were created
        self.assertEqual(EncryptionReason.objects.count(), 0)

    def test_first_profile_is_set_as_author(self):
        # Ensure there is more than one profile in the database
        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password",
        )

        # Call the function
        populate_encryption_reasons(self.encryption_reasons)

        # Check that the first profile is set as the author for all encryption reasons
        for encryption_reason in EncryptionReason.objects.all():
            self.assertEqual(encryption_reason.author, self.profile)


class TestIsProfilesGroupLeader(TestCase):
    def setUp(self):
        # Create users and profiles
        self.leader_user = User.objects.create_user(
            email="leader@example.com",
            password="password",
        )
        self.leader_profile = self.leader_user.profile

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="password",
        )
        self.other_profile = self.other_user.profile

        # Create a group with leader_profile as the leader
        self.group = Group.objects.create(
            name="Test Group",
            leader=self.leader_profile,
        )

        # Add other_profile to the group as a member
        self.group_member = GroupMember.objects.create(
            group=self.group,
            profile=self.other_profile,
        )

    def test_user_is_group_leader_of_own_group(self):
        """
        Test if the function returns True when the user is the leader
        of their own group.
        """
        result = is_profiles_group_leader(
            self.leader_user,
            self.leader_profile,
        )
        self.assertTrue(result)

    def test_user_is_not_group_leader(self):
        """
        Test if the function returns False when the user is not the
        leader of any group.
        """
        another_user = User.objects.create_user(
            email="another@example.com",
            password="password",
        )

        result = is_profiles_group_leader(
            another_user,
            self.other_profile,
        )
        self.assertFalse(result)

    def test_user_is_leader_of_group_containing_profile(self):
        """
        Test if the function returns True when the user is the leader
        of the group containing the profile.
        """
        result = is_profiles_group_leader(
            self.leader_user,
            self.other_profile,
        )
        self.assertTrue(result)

    def test_user_is_leader_but_profile_not_in_group(self):
        """
        Test if the function returns False when the user is the leader
        of a group but the profile is not in the group.
        """
        user = User.objects.create_user(
            email="newuser@example.com",
            password="password",
        )

        if Profile.objects.filter(user=user).exists():
            Profile.objects.filter(user=user).delete()

        new_profile = Profile.objects.create(user=user)

        result = is_profiles_group_leader(
            self.leader_user,
            new_profile,
        )
        self.assertFalse(result)
