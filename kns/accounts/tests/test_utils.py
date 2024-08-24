import pytest
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from kns.custom_user.models import User

from .. import utils


@pytest.fixture
def user_factory():
    def create_user(
        email="testuser@example.com",
        password="testpassword",
    ):
        return User.objects.create_user(
            email=email,
            password=password,
        )

    return create_user


class TestUtils:
    def test_compare_passwords(self):
        """
        Test the compare_passwords function for various scenarios.
        """
        # Test with matching passwords
        assert utils.compare_passwords(
            "password123",
            "password123",
        )

        # Test with non-matching passwords
        assert not utils.compare_passwords(
            "password123",
            "password456",
        )

        # Test with empty passwords
        assert not utils.compare_passwords(
            "",
            "password456",
        )
        assert not utils.compare_passwords(
            "password123",
            "",
        )
        assert utils.compare_passwords(
            "",
            "",
        )

    def test_generate_verification_token(self, user_factory):
        """
        Test the generate_verification_token function.
        """
        user = user_factory()  # Use a user factory to create a user object
        token = utils.generate_verification_token(user)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token(self, user_factory):
        """
        Test the verify_token function for valid and invalid tokens.
        """
        user = user_factory()  # Use a user factory to create a user object
        valid_token = utils.generate_verification_token(user)

        # Test with a valid token
        assert utils.verify_token(user, valid_token)

        # Test with an invalid token
        assert not utils.verify_token(user, "invalidtoken")

    def test_decode_uid(self, user_factory):
        """
        Test the decode_uid function for valid and invalid UID strings.
        """
        user = user_factory()  # Use a user factory to create a user object
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        # Test with a valid UID
        decoded_uid = utils.decode_uid(uidb64)
        assert decoded_uid == str(user.pk)

        # Test with an invalid UID
        assert utils.decode_uid("invaliduid") is None

        # Test with an empty UID
        assert utils.decode_uid("") is None
