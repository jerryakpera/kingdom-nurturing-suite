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
