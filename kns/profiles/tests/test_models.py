import pytest

from kns.custom_user.models import User
from kns.groups.models import Group
from kns.groups.tests import test_constants
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


def test_profile_get_role_display_str(user):
    """
    Test that the get_role_display_str method returns the correct
    string representation for the profile's role.
    """
    profile = Profile.objects.get(user=user)

    # Test when role is "member"
    profile.role = "member"
    profile.save()
    assert profile.get_role_display_str() == "Member"

    # Test when role is "leader"
    profile.role = "leader"
    profile.save()
    assert profile.get_role_display_str() == "Leader"

    # Test when role is "external_person"
    profile.role = "external_person"
    profile.save()
    assert profile.get_role_display_str() == "External Person"


def test_profile_str_method(user):
    """
    Test that the __str__ method returns the full name of the profile.
    """
    profile = Profile.objects.get(user=user)

    profile.last_name = "Doe"
    profile.first_name = "John"

    profile.save()

    assert str(profile) == "John Doe"


def test_profile_is_leading_group(user):
    """
    Test that the __str__ method returns the full name of the profile.
    """
    profile = Profile.objects.get(user=user)

    profile.first_name = "John"
    profile.last_name = "Doe"
    profile.gender = "Male"
    profile.date_of_birth = "1990-01-01"
    profile.place_of_birth_country = "USA"
    profile.place_of_birth_city = "New York"
    profile.location_country = "USA"
    profile.location_city = "New York"
    profile.role = "leader"
    profile.slug = "john-doe"

    user.verified = True
    user.agreed_to_terms = True

    profile.save()
    user.save()

    Group.objects.create(
        leader=profile,
        name="Test Group",
        slug="test-group",
        description=test_constants.VALID_GROUP_DESCRIPTION,
    )

    assert profile.is_leading_group()
