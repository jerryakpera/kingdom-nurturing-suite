"""
This module contains various constants used throughout the application.

Constants:
- GENDER_OPTIONS: List of tuples representing gender options for user profiles.
- PROFILE_ROLE_OPTIONS: List of tuples representing different roles a profile can have.
"""

# GENDER_OPTIONS
# List of tuples representing gender options for user profiles.
# Each tuple contains a value and a human-readable name.
GENDER_OPTIONS = [
    ("male", "Male"),
    ("female", "Female"),
]

REGISTER_MEMBER_FORM_STEPS = [
    {
        "index": 1,
        "title": "Bio details",
        "subtitle": (
            "Enter the bio details of the person you would "
            "like to add to your group."
        ),
        "description": (
            "We allow you to hide the user's sensitive information and"
            " encrypt their name to allow others to interact with their "
            "profile without revealing their identity."
        ),
    },
    {
        "index": 2,
        "title": "Contact details",
        "subtitle": (
            "Provide information on how we can reach other disciples"
            " can reach this person."
        ),
        "description": (
            "Although providing a location is optional, please note "
            "that location details will enhance their KNT experience "
            "by allowing us to make personalized recommendations "
            "to the user."
        ),
    },
    {
        "index": 3,
        "title": "Involvement details",
        "subtitle": (
            "Indicate if the person is willing and able to be involved "
            "in different aspects of KNT."
        ),
        "description": (
            "We require a reason for people unwilling or unable to train"
            " or mentor others. Having this reason will allow us to "
            "offer growth solutions and to prevent them from receiving "
            "invitations to facilitate training and mentorship."
        ),
    },
    {
        "index": 4,
        "title": "Select role",
        "subtitle": ("Select the user's role"),
        "description": (
            "In this step, you can select the role of the member. "
            "Member roles are profiles that are currently not leading "
            "their own DBS/DMM groups. Leader roles are those currently "
            "leading their own groups, and external persons are "
            "individuals with skills and expertise that can be useful "
            "to other disciples but will not manage their own profile."
        ),
    },
]


# PROFILE_ROLE_OPTIONS
# List of tuples representing different roles a profile can have.
# Each tuple contains a role value and a human-readable name.
PROFILE_ROLE_OPTIONS = [
    ("member", "Member"),
    ("leader", "Leader"),
    ("external_person", "External Person"),
]

REJECT_REASON_MIN_LENGTH = 100
REJECT_REASON_MAX_LENGTH = 500
