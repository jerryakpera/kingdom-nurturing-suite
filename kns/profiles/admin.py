"""
Django admin site configuration for the profiles app.
"""

from django.contrib import admin

from kns.skills.models import ProfileInterest, ProfileSkill

from .models import ConsentForm, Profile


class ProfileSkillInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileSkill model.

    This allows the skills associated with a profile to be managed
    directly within the Profile admin interface.
    """

    extra = 0
    model = ProfileSkill


class ProfileInterestInline(admin.TabularInline):
    """
    Inline admin interface for the ProfileInterest model.

    This allows the interests associated with a profile to be managed
    directly within the Profile admin interface.
    """

    extra = 0
    model = ProfileInterest


class ConsentFormInline(admin.StackedInline):
    """
    Inline admin interface for the ConsentForm model.

    This allows the consent form associated with a profile to be edited
    directly within the Profile admin interface.
    """

    model = ConsentForm
    fk_name = "profile"
    extra = 0


class ProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for the Profile model.

    Displays and manages the profile information, including the inline
    consent form, skills, and interests.
    """

    inlines = [
        ProfileSkillInline,
        ProfileInterestInline,
        ConsentFormInline,
    ]


# Register the ConsentForm model with the admin site
admin.site.register(ConsentForm)

# Register the ProfileAdmin with the admin site
admin.site.register(Profile, ProfileAdmin)
