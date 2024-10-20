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
EVENT_DEFAULT_REGISTRATION_LIMIT = 1000

# Minimum days in the future for event start date
EVENT_MIN_DAYS_IN_FUTURE = 3

EVENT_SUMMARY_MAX_LENGTH = 300
EVENT_SUMMARY_MIN_LENGTH = 135
EVENT_TITLE_MAX_LENGTH = 135
EVENT_TITLE_MIN_LENGTH = 15

HELP_TEXT_CONTACT_NAME = "Enter the name of the event contact."
HELP_TEXT_CONTACT_EMAIL = "Enter the email address of the event contact (optional)."

# Constants for Event Location Form
HELP_TEXT_CITY = "Enter the city where the event will be held."
HELP_TEXT_COUNTRY = "Select the country where the event will be held."


MAX_TAGS = 5


REGISTRATION_LIMIT_ERROR_MESSAGE = "Registration limit must be a positive integer."
ZERO_REGISTRATION_LIMIT_ERROR_MESSAGE = "Registration limit must be at least 1."


ERROR_CONTACT_NAME_REQUIRED = "Enter the name of the contact person."
ERROR_CONTACT_EMAIL_REQUIRED = "Enter the email address of the contact person."

stepper_steps = [
    {
        "no": 1,
        "title": "Add details to your event",
        "description": (
            "Provide basic details about your event such as the title, "
            "summary, and description. This helps attendees understand "
            "what your event is about."
        ),
        "form_class": "EventContentForm",
        "fields": ["title", "summary", "description", "tags"],
    },
    {
        "no": 2,
        "title": "Event Dates",
        "description": (
            "Specify when your event will start and end. Accurate"
            " dates ensure proper scheduling and notifications."
        ),
        "form_class": "EventDatesForm",
        "fields": ["start_date", "end_date"],
    },
    {
        "no": 3,
        "title": "Event Location",
        "description": (
            "Set the location for your event, including the country"
            " and city. Attendees will need this information to attend "
            "in person or know if the event is virtual."
        ),
        "form_class": "EventLocationForm",
        "fields": ["country", "city", "address", "is_online"],
    },
    {
        "no": 4,
        "title": "Event Miscellaneous",
        "description": (
            "Add additional details like refreshments and accommodation"
            " if they are available for the event. These options help attendees plan ahead."
        ),
        "form_class": "EventMiscForm",
        "fields": ["refreshments", "accommodation"],
    },
    {
        "no": 5,
        "title": "Event Contact",
        "description": (
            "Provide contact information for the event organizer. "
            "Attendees may need this for questions or further communication."
        ),
        "form_class": "EventContactForm",
        "fields": ["event_contact_name", "event_contact_email", "event_contact_phone"],
    },
]
