"""
Constants for the `core` app.
"""

DEFAULT_DESCRIPTION_LENGTH = 500
DEFAULT_DESCRIPTION_MIN_LENGTH = 100
DEFAULT_DESCRIPTION_MAX_LENGTH = 500

MENTORSHIP_GOAL_TYPES = [
    ("Primary", "Primary"),
    ("Secondary", "Secondary"),
]

MENTORSHIP_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("pending", "Pending Approval"),
    ("active", "Active"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
]

BOOLEAN_CHOICES = [
    (True, "Yes"),
    (False, "No"),
]

GENDER_OPTIONS = [
    ("Male", "Male"),
    ("Female", "Female"),
]

ARTICLE_TYPE_CHOICES = [
    ("story", "Story"),
    ("testimony", "Testimony"),
    ("good_practice", "Good practice"),
    ("prayer_request", "Prayer request"),
]

PROFILE_ROLE_OPTIONS = [
    ("member", "Member"),
    ("leader", "Leader"),
    ("external_person", "External Person"),
]

STATUS_CHOICES = [
    ("draft", "Draft"),
    ("published", "Published"),
    ("archived", "Archived"),
]

ACTIVITY_TYPE = [
    ("skill_training", "Skill Training"),
    ("movement_training", "Movement Training"),
    ("community_service", "Community Service"),
    ("prayer_movement", "Prayer Movement"),
]

EVENT_REGISTRATION_CHOICES = [
    (
        "attending",
        "Attending",
    ),
    (
        "undecided",
        "Undecided",
    ),
]

DISCIPLESHIP_GROUP_CHOICES = [
    ("Group member", "Group member"),
    ("First 12", "First 12"),
    ("First 3", "First 3"),
    ("Sent forth", "Sent forth"),
]

DEFAULT_ADULT_AGE = 16
MIN_REGISTRATION_AGE = 13

MAX_SKILLS_USER = 5
MAX_INTERESTS_USER = 10
MIN_SKILLS_TRAINING = 1
MAX_SKILLS_TRAINING = 7
MIN_MOVEMENTS_TRAINING = 1
MAX_MOVEMENTS_TRAINING = 7

MAX_MENTORS_USER = 3
MAX_MENTEES_USER = 3
MAX_GOALS_MENTORSHIP = 5
MAX_MENTORSHIP_AREAS_USER = 5
MENTORSHIP_PROHIBITION_WEEKS = 4
MIN_MENTORSHIP_DURATION_WEEKS = 4
MAX_MENTORSHIP_DURATION_WEEKS = 12

CONTACT_VISIBILITY = True

CHANGE_ROLE_PERMISSION_REQUIRED = True
PUBLISH_EVENT_PERMISSION_REQUIRED = True
START_MENTORSHIP_PERMISSION_REQUIRED = True
ADD_GROUP_MEMBER_PERMISSION_REQUIRED = True
PUBLISH_TESTIMONY_PERMISSION_REQUIRED = True
PUBLISH_GOOD_PRACTICE_PERMISSION_REQUIRED = True
PUBLISH_PRAYER_REQUEST_PERMISSION_REQUIRED = True

EVENT_REGISTRATION_LIMIT = 50
ORGANIZER_MUST_FACILITATE = True
MIN_DAYS_TO_MODIFY_SENSITIVE_CONTENT = 7

CHANGE_ROLE_TO_LEADER_ACTION_TYPE = "change_role_to_leader"
