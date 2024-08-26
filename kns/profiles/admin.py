"""
Django admin site configuration for the profiles app.
"""

from django.contrib import admin

from .models import ConsentForm, Profile


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
    consent form.
    """

    inlines = [ConsentFormInline]


# Register the ConsentForm model with the admin site
admin.site.register(ConsentForm)

# Register the ProfileAdmin with the admin site
admin.site.register(Profile, ProfileAdmin)
