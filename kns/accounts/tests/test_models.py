from kns.accounts.tests.factories import UserFactory


class TestUser:
    def test_factory(self):
        user = UserFactory()

        # bandit: disable=B101
        assert user is not None
