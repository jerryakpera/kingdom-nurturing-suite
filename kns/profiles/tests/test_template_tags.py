from django.test import TestCase

from ..templatetags import get_nth_element


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
