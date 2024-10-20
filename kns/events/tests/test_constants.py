"""
Test constants for the `events` app forms.
"""

from .. import constants

# Event Title Constants
EVENT_TITLE = "Valid Event Title"
SHORT_EVENT_TITLE = "Short"
LONG_EVENT_TITLE = "A" * (constants.EVENT_TITLE_MAX_LENGTH + 1)

# Event Summary Constants
EVENT_SUMMARY = "This is a valid event summary."
SHORT_EVENT_SUMMARY = "Short"
LONG_EVENT_SUMMARY = "B" * (constants.EVENT_SUMMARY_MAX_LENGTH + 1)

# Event Description Constants
EVENT_DESCRIPTION = "This is a detailed description of the event."
SHORT_EVENT_DESCRIPTION = "Short description."
LONG_EVENT_DESCRIPTION = "C" * 1000

# Event Dates
VALID_START_DATE = "2024-01-05"
VALID_END_DATE = "2024-01-06"
PAST_START_DATE = "2023-10-01"
INVALID_END_DATE = "2024-01-04"

# Location Constants
VALID_CITY = "Lagos"
INVALID_CITY = ""
VALID_COUNTRY = "NG"
INVALID_COUNTRY = ""

# Contact Information Constants
VALID_CONTACT_NAME = "John Doe"
SHORT_CONTACT_NAME = "JD"
LONG_CONTACT_NAME = "D" * (
    constants.EVENT_CANCEL_REASON_MAX_LENGTH + 1
)  # Exceeding max length
VALID_CONTACT_EMAIL = "contact@example.com"
INVALID_CONTACT_EMAIL = "invalid-email"  # Invalid email format

# Miscellaneous Constants
VALID_REFRESHMENTS = "True"
INVALID_REFRESHMENTS = "Not a boolean"
VALID_ACCOMMODATION = "False"

# Registration Limits
VALID_REGISTRATION_LIMIT = 100
ZERO_REGISTRATION_LIMIT = 0  # Invalid limit
NEGATIVE_REGISTRATION_LIMIT = -10  # Invalid limit

# Tags
VALID_TAGS = ["tag1", "tag2", "tag3"]
TOO_MANY_TAGS = [
    "tag1",
    "tag2",
    "tag3",
    "tag4",
    "tag5",
    "tag6",
]
