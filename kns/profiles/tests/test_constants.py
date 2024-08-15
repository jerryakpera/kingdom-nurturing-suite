from ..constants import GENDER_OPTIONS, PROFILE_ROLE_OPTIONS


def test_gender_options():
    """
    Test that the GENDER_OPTIONS constant is defined correctly.
    """
    expected_gender_options = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    assert (
        GENDER_OPTIONS == expected_gender_options
    ), f"Expected {expected_gender_options}, but got {GENDER_OPTIONS}"


def test_profile_role_options():
    """
    Test that the PROFILE_ROLE_OPTIONS constant is defined correctly.
    """
    expected_profile_role_options = [
        ("member", "Member"),
        ("leader", "Leader"),
        ("external_person", "External Person"),
    ]
    assert (
        PROFILE_ROLE_OPTIONS == expected_profile_role_options
    ), f"Expected {expected_profile_role_options}, but got {PROFILE_ROLE_OPTIONS}"
