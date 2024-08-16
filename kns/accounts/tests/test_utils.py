from ..utils import compare_passwords


class TestUtils:
    def test_compare_passwords(self):
        """
        Test the compare_passwords function for various scenarios.
        """
        # Test with matching passwords
        assert compare_passwords(
            "password123",
            "password123",
        )

        # Test with non-matching passwords
        assert not compare_passwords(
            "password123",
            "password456",
        )

        # Test with empty passwords
        assert not compare_passwords("", "password456")
        assert not compare_passwords("password123", "")
        assert compare_passwords("", "")
