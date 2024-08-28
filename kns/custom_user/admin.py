"""
Django admin configuration for the user model.
"""

from django.contrib import admin
from django_use_email_as_username.admin import BaseUserAdmin

from .models import User


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for the User model.
    """

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": ("verified", "is_visitor", "agreed_to_terms"),
            },
        ),
    )

    # If you want to include these fields in the list display in the admin panel
    list_display = BaseUserAdmin.list_display + (
        "verified",
        "agreed_to_terms",
    )


# Register the User model with the custom admin class
admin.site.register(User, CustomUserAdmin)
