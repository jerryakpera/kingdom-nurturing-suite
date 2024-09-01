"""
Admin configuration for the FaithMilestone model.
"""

from django.contrib import admin

from .models import FaithMilestone


class FaithMilestoneAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the FaithMilestone model.
    Configures the display of FaithMilestone objects in the Django admin.
    """

    list_display = ["title", "type"]


# Register the FaithMilestone model with the custom admin interface
admin.site.register(FaithMilestone, FaithMilestoneAdmin)
