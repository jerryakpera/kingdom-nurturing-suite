"""
Django admin site configuration for the profiles app.
"""

from django.contrib import admin

from kns.classifications.models import ProfileClassification
from kns.discipleships.models import Discipleship
from kns.faith_milestones.models import ProfileFaithMilestone
from kns.levels.models import ProfileLevel
from kns.mentorships.models import ProfileMentorshipArea
from kns.onboarding.models import ProfileCompletionTask
from kns.skills.models import ProfileInterest, ProfileSkill
from kns.vocations.models import ProfileVocation

from .models import ConsentForm, EncryptionReason, Profile, ProfileEncryption


class ProfileEncryptionInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileEncryption model.

    This allows the encryption associated with a profile to be managed
    directly within the Profile admin interface.
    """

    extra = 0
    model = ProfileEncryption
    fk_name = "profile"


class ProfileMentorshipAreaInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileMentorshipArea model.
    """

    extra = 0
    model = ProfileMentorshipArea
    fk_name = "profile"


class ProfileVocationInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileVocation model.

    This allows the vocations associated with a profile to be managed
    directly within the Profile admin interface.
    """

    extra = 0
    model = ProfileVocation
    fk_name = "profile"


class ProfileSkillInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileSkill model.

    This allows the skills associated with a profile to be managed
    directly within the Profile admin interface.
    """

    extra = 0
    model = ProfileSkill


class ProfileDisciplesInline(admin.TabularInline):
    """
    Inline admin interface for the Discipleship model.

    This allows the disciples to be associated with the discipler.
    """

    model = Discipleship
    fk_name = "discipler"
    extra = 0


class ProfileInterestInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileInterest model.

    This allows the interests associated with a profile to be managed
    directly within the Profile admin interface.
    """

    extra = 0
    model = ProfileInterest


class ProfileFaithMilestoneInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileFaithMilestone model.

    This allows the faith milestones associated with a profile to be managed
    directly within the Profile admin interface.
    """

    extra = 0
    model = ProfileFaithMilestone


class ConsentFormInline(admin.StackedInline):
    """
    Inline admin interface for the ConsentForm model.

    This allows the consent form associated with a profile to be edited
    directly within the Profile admin interface.
    """

    model = ConsentForm
    fk_name = "profile"
    extra = 0


class ProfileLevelInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileLevel model.

    This allows the levels and sublevels associated with a profile to be
    edited directly within the Profile admin interface.
    """

    extra = 1
    model = ProfileLevel


class ProfileClassificationInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileClassification model.

    This allows the classifications and subclassifications associated with a profile to be
    edited directly within the Profile admin interface.
    """

    extra = 1
    model = ProfileClassification


class ProfileCompletionTaskInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileCompletionTask model.
    """

    extra = 0
    model = ProfileCompletionTask


class ProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for the Profile model.

    Displays and manages the profile information, including the inline
    consent form, skills, and interests.
    """

    list_display = [
        "get_real_name",
        "email",
        "get_role_display_str",
    ]

    inlines = [
        ProfileSkillInline,
        ProfileInterestInline,
        ProfileMentorshipAreaInline,
        ConsentFormInline,
        ProfileEncryptionInline,
        ProfileFaithMilestoneInline,
        ProfileDisciplesInline,
        ProfileVocationInline,
        ProfileLevelInline,
        ProfileClassificationInline,
        ProfileCompletionTaskInline,
    ]


# Register the ProfileAdmin with the admin site
admin.site.register(Profile, ProfileAdmin)

admin.site.register(ConsentForm)
admin.site.register(EncryptionReason)
