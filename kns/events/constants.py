"""
Constant values for the `events` app.
"""

ERROR_START_DATE_FUTURE = "The start date must be at least 3 days in the future."
ERROR_END_DATE = "The end date cannot be before the start date."
ERROR_REGISTRATION_DEADLINE = (
    "The registration deadline date must be before the event start date."
)


EVENT_CANCEL_REASON_MIN_LENGTH = 135
EVENT_CANCEL_REASON_MAX_LENGTH = 300

EVENT_DEFAULT_REGISTRATION_LIMIT = 50

# Minimum days in the future for event start date
EVENT_MIN_DAYS_IN_FUTURE = 3

EVENT_SUMMARY_MIN_LENGTH = 135
EVENT_SUMMARY_MAX_LENGTH = 300

EVENT_TITLE_MIN_LENGTH = 15
EVENT_TITLE_MAX_LENGTH = 135

MAX_TAGS = 5
