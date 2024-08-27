"""
Django admin site configuration for the core app.
"""

from django.contrib import admin

from .models import FAQ, MakeLeaderActionApproval, Setting

# Registering the FAQ model with the admin site
admin.site.register(FAQ)

# Registering the Setting model with the admin site
admin.site.register(Setting)


class MakeLeaderActionApprovalAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the `MakeLeaderActionApproval` model.

    This configuration sets the `new_leader` field as read-only in the
    admin interface.
    """

    readonly_fields = ("new_leader",)


# Registering the MakeLeaderActionApproval model with the custom admin
# configuration
admin.site.register(MakeLeaderActionApproval, MakeLeaderActionApprovalAdmin)
