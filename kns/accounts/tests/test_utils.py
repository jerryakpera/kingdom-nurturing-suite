from django.test import TestCase

from ..utils import compare_passwords


class UtilsTests(TestCase):
    def test_compare_passwords(self):
        """
        Test the compare_passwords function for various scenarios.
        """
        # Test with matching passwords
        self.assertTrue(
            compare_passwords(
                "password123",
                "password123",
            )
        )

        # Test with non-matching passwords
        self.assertFalse(
            compare_passwords(
                "password123",
                "password456",
            )
        )

        # Test with empty passwords
        self.assertFalse(compare_passwords("", "password456"))
        self.assertFalse(compare_passwords("password123", ""))
        self.assertTrue(compare_passwords("", ""))
