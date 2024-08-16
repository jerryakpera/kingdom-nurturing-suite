import pytest

from kns.custom_user.models import User
from kns.profiles.models import Profile


@pytest.fixture
def user():
    """
    Fixture to create a test user.
    """
    return User.objects.create_user(
        email="testuser@example.com",
        password="testpassword",
    )


def test_profile_creation_on_user_creation(user):
    """
    Test that a Profile instance is created when a User instance is created.
    """
    profile = Profile.objects.get(user=user)

    assert profile is not None
    assert profile.email == user.email


def test_profile_email_unique_constraint():
    """
    Test that the email field on the Profile model is unique.
    """
    User.objects.create_user(email="uniqueuser@example.com", password="testpassword")

    with pytest.raises(Exception) as excinfo:
        User.objects.create_user(
            email="uniqueuser@example.com", password="anotherpassword"
        )

    assert "UNIQUE constraint failed" in str(excinfo.value)


def test_profile_created_at_exists(user):
    """
    Test that the created_at field exists on the profile instance.
    """
    profile = Profile.objects.get(user=user)

    assert profile.created_at is not None


def test_profile_updated_at_exists(user):
    """
    Test that the updated_at field exists on the profile instance.
    """
    profile = Profile.objects.get(user=user)

    assert profile.updated_at is not None


def test_profile_verified_exists(user):
    """
    Test that the verified field exists on the profile instance.
    """
    profile = Profile.objects.get(user=user)

    assert profile.verified is not None
    assert not profile.verified


def test_profile_is_visitor_exists(user):
    """
    Test that the is_visitor field exists on the profile instance.
    """
    profile = Profile.objects.get(user=user)

    assert profile.is_visitor is not None
    assert not profile.is_visitor


def test_profile_agreed_to_terms_exists(user):
    """
    Test that the agreed_to_terms field exists on the profile instance.
    """
    profile = Profile.objects.get(user=user)

    assert profile.agreed_to_terms is not None
    assert not profile.agreed_to_terms


def test_profile_role_exists(user):
    """
    Test that the role field exists on the profile instance.
    """
    profile = Profile.objects.get(user=user)

    assert profile.role is not None
    assert profile.role in [
        "member",
        "leader",
        "external_person",
    ]
