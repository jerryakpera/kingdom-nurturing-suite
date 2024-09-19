"""
Constants for the `onboarding` app.
"""

ONBOARDING_STEPS = {  # pragma: no cover
    "profile": {
        "no": 1,
        "name": "Profile details",
        "title": "Welcome to KNS - Kingdom Nurturing Suite",
        "subtitle": "We have prepared a short process to get you all set up on KNS.",
        "description": (
            "To unlock its full potential, take a few minutes to "
            "complete your onboarding process."
        ),
        "items": [
            "confirming your profile",
            "adding your skills and interests to connect with like-minded people",
            "registering your group for easy management of members",
            "and reviewing and agreeing to our Terms and Conditions.",
        ],
        "link": "/onboarding",
        "url_name": "onboarding:index",
        "template_name": "onboarding/index.html",
    },
    "involvement": {
        "no": 2,
        "name": "Involvement preferences",
        "title": "Empowerment Through Mentorship and Training",
        "subtitle": "Join the Global Network of Disciples",
        "description": ("Indicate your willingness to share skills and mentor others."),
        "items": [
            "Facilitate mentorship relationships.",
            "Manage discipleship of your members.",
            "Register members for skill trainings.",
            "Access movement trainings.",
        ],
        "link": "/onboarding/involvement",
        "url_name": "onboarding:involvement",
        "template_name": "onboarding/involvement_onboarding.html",
    },
    "group": {
        "no": 3,
        "name": "Group registration",
        "title": "Register your group",
        "subtitle": "A Kingdom Nurturing group can be a DBS group or a discipleship group.",
        "description": (
            "By registering your group on the app, you're "
            "fostering deeper connections."
        ),
        "items": [
            "Facilitate mentorship relationships.",
            "Manage discipleship of your members.",
            "Register members for skill trainings.",
            "Access movement trainings.",
        ],
        "link": "/onboarding/group",
        "url_name": "onboarding:group",
        "template_name": "onboarding/register_group_onboarding.html",
    },
    "agree": {
        "no": 4,
        "name": "Terms and Conditions",
        "title": "Agree to our Terms and Conditions",
        "subtitle": (
            "Before you continue, please read and agree to our terms and conditions."
        ),
        "description": (
            "By agreeing, you accept the rules governing the use of our platform."
        ),
        "items": [
            "Review our terms and conditions.",
            "Agree to abide by the terms to proceed.",
            "Gain full access to the platform.",
        ],
        "link": "/onboarding/agree",
        "url_name": "onboarding:agree",
        "template_name": "onboarding/agree_onboarding.html",
    },
}


TASKS_CHOICES = [  # pragma: no cover
    (
        "complete_profile",
        "Complete your profile",
    ),
    (
        "register_group",
        "Register group",
    ),
    (
        "register_first_member",
        "Register first member",
    ),
    (
        "add_vocations_skills",
        "Add vocations, skills, and interests",
    ),
    (
        "browse_events",
        "Browse events near you",
    ),
]

TASKS = {
    "complete_profile": {
        "task_name": "complete_profile",
        "task_description": (
            "Complete your profile by providing necessary fields "
            "to ensure that your profile is complete and fully representative of you."
        ),
    },
    "register_group": {
        "task_name": "register_group",
        "task_description": (
            "Register your group that you are leading. Ensure that all necessary "
            "details are provided, such as the group's name, description, and location."
        ),
    },
    "register_first_member": {
        "task_name": "register_first_member",
        "task_description": (
            "Register the first member of your newly created group. This process "
            "involves adding a member to the group and ensuring their details "
            "are correctly entered."
        ),
    },
    "add_vocations_skills": {
        "task_name": "add_vocations_skills",
        "task_description": (
            "Add vocations, skills, and interests to your profile. This helps "
            "in showcasing your expertise and areas of interest, which "
            "is vital for matching you with relevant opportunities and networks."
        ),
    },
    "browse_events": {
        "task_name": "browse_events",
        "task_description": (
            "Browse through events that are happening near you. This "
            "includes viewing skill and movement trainings, prayer movements "
            "and community services."
        ),
    },
}
