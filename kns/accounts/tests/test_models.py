from kns.accounts.tests.factories import UserFactory


class TestUser:
    def test_factory(self):
        """
        The factory produces a valid instance.
        """
        user = UserFactory()

        # bandit: disable=B101
        assert user is not None
        assert user.profile is not None
