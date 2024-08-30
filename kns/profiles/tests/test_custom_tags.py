from django.test import TestCase

from kns.custom_user.models import User
from kns.groups.models import Group

from ..templatetags import can_edit_profile, get_nth_element, name_with_apostrophe


class GetNthElementFilterTest(TestCase):
    def test_valid_index(self):
        """Test that the filter returns the correct element for a valid index."""
        lst = ["apple", "banana", "cherry"]
        self.assertEqual(get_nth_element(lst, 0), "apple")
        self.assertEqual(get_nth_element(lst, 1), "banana")
        self.assertEqual(get_nth_element(lst, 2), "cherry")

    def test_invalid_index(self):
        """Test that the filter returns None for an out-of-range index."""
        lst = ["apple", "banana", "cherry"]
        self.assertIsNone(get_nth_element(lst, 3))  # Index out of range
        self.assertIsNone(get_nth_element(lst, -4))  # Negative index out of range

    def test_empty_list(self):
        """Test that the filter returns None for an empty list."""
        lst = []
        self.assertIsNone(get_nth_element(lst, 0))
        self.assertIsNone(get_nth_element(lst, 1))

    def test_string_as_list(self):
        """Test that the filter returns the correct character for a string treated as a list."""
        string = "hello"
        self.assertEqual(get_nth_element(string, 0), "h")
        self.assertEqual(get_nth_element(string, 4), "o")
        self.assertIsNone(get_nth_element(string, 5))  # Out of range

    def test_non_integer_index(self):
        """Test that the filter returns None for a non-integer index."""
        lst = ["apple", "banana", "cherry"]
        self.assertIsNone(get_nth_element(lst, "a"))  # Non-integer index
        self.assertIsNone(get_nth_element(lst, None))  # None as index
        self.assertIsNone(get_nth_element(lst, "1.5"))  # Float string as index


class CanEditProfileFilterTest(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="testpassword",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="testpassword",
        )
        self.user3 = User.objects.create_user(
            email="user3@example.com",
            password="testpassword",
        )

        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.profile3 = self.user3.profile

        # Set roles
        self.profile1.role = "leader"
        self.profile2.role = "member"
        self.profile3.role = "leader"

        # Save profiles
        self.profile1.save()
        self.profile2.save()
        self.profile3.save()

        self.group = Group.objects.create(
            leader=self.profile1,
            name="Test Group",
            slug="test-group",
            description="Test Description",
        )

        # Assign groups
        self.group.add_member(self.profile2)

    def test_can_edit_own_profile(self):
        """Test that a user can edit their own profile."""
        self.assertTrue(
            can_edit_profile(self.user1, self.profile1),
        )

    def test_leader_with_password_cannot_edit_another_leader(self):
        """Test that a leader with a usable password cannot edit another leader's profile."""
        self.user3.set_password("testpassword")
        self.user3.save()

        self.assertFalse(
            can_edit_profile(
                self.user1,
                self.profile3,
            ),
        )

    def test_user_not_in_leader_group_cannot_edit(self):
        """Test that a user not in the leader's group cannot edit another user's profile."""
        self.assertFalse(
            can_edit_profile(
                self.user2,
                self.profile3,
            ),
        )

    def test_leader_can_edit_member_in_group(self):
        """Test that a leader can edit a member's profile in their group."""
        self.assertTrue(
            can_edit_profile(
                self.user1,
                self.profile2,
            ),
        )

    def test_leader_cannot_edit_member_not_in_group(self):
        """Test that a leader cannot edit a member's profile if they
        are not in the leader's group."""
        self.assertFalse(
            can_edit_profile(
                self.user1,
                self.profile3,
            ),
        )

    def test_user_without_group_led_cannot_edit(self):
        """Test that a user without the group_led attribute on their
        profile cannot edit another user's profile."""
        self.assertFalse(
            can_edit_profile(
                self.user2,
                self.profile3,
            ),
        )


class NameWithApostropheFilterTest(TestCase):
    def setUp(self):
        """Set up any necessary data for the tests."""
        pass

    def test_name_without_trailing_s(self):
        """Test that the filter correctly adds 's for names that do not end in s."""
        self.assertEqual(name_with_apostrophe("John"), "John's")
        self.assertEqual(name_with_apostrophe("Alice"), "Alice's")

    def test_name_with_trailing_s(self):
        """Test that the filter correctly adds an apostrophe for names that end in s."""
        self.assertEqual(name_with_apostrophe("James"), "James'")
        self.assertEqual(name_with_apostrophe("Moses"), "Moses'")

    def test_empty_name(self):
        """Test that the filter returns an empty string for an empty name."""
        self.assertEqual(name_with_apostrophe(""), "")

    def test_name_with_apostrophe_in_the_middle(self):
        """Test that the filter handles names with an apostrophe correctly."""
        self.assertEqual(name_with_apostrophe("O'Neil"), "O'Neil's")
        self.assertEqual(name_with_apostrophe("D'Arcy"), "D'Arcy's")
