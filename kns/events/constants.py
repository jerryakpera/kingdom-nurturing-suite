"""
Constant values for the `events` app.
"""

ERROR_END_DATE = "The end date cannot be before the start date."
ERROR_NO_COUNTRY_AND_CITY = "Both country and city fields are required."
ERROR_NO_LOCATION_CITY = "Select the city where the event will be held."
ERROR_NO_LOCATION_COUNTRY = "Select the country where the event will be held."
ERROR_REGISTRATION_DEADLINE = (
    "The registration deadline date must be before the event start date."
)
ERROR_START_DATE_FUTURE = "The start date must be at least 3 days in the future."

EVENT_CANCEL_REASON_MAX_LENGTH = 300
EVENT_CANCEL_REASON_MIN_LENGTH = 135
EVENT_DEFAULT_REGISTRATION_LIMIT = 50

# Minimum days in the future for event start date
EVENT_MIN_DAYS_IN_FUTURE = 3

EVENT_SUMMARY_MAX_LENGTH = 300
EVENT_SUMMARY_MIN_LENGTH = 135
EVENT_TITLE_MAX_LENGTH = 135
EVENT_TITLE_MIN_LENGTH = 15

# Constants for Event Location Form
HELP_TEXT_CITY = "Enter the city where the event will be held."
HELP_TEXT_COUNTRY = "Select the country where the event will be held."
MAX_TAGS = 5


REGISTRATION_LIMIT_ERROR_MESSAGE = "Registration limit must be a positive integer."
