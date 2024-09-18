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
