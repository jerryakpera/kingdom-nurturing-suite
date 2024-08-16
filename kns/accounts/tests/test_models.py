from kns.accounts.tests.factories import UserFactory
from kns.custom_user.models import User


class TestUser:
    def test_factory(self):
        """
        The factory produces a valid instance.
        """
        user = UserFactory()

        # bandit: disable=B101
        assert user is not None
        assert user.profile is not None

    def test_user_verified_field_exists(user):
        """
        Test that the verified field exists on the user instance.
        """
        user = UserFactory()

        assert user.verified is not None
        assert not user.verified

    def test_user_is_visitor_field_exists(user):
        """
        Test that the is_visitor field exists on the user instance.
        """
        user = UserFactory()

        assert user.is_visitor is not None
        assert not user.is_visitor

    def test_user_agreed_to_terms_field_exists(user):
        """
        Test that the agreed_to_terms field exists on the user instance.
        """
        user = UserFactory()

        assert user.agreed_to_terms is not None
        assert not user.agreed_to_terms
