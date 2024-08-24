"""
Django admin configuration for the `groups` app.
"""

from django.contrib import admin

from .models import Group, GroupMember


class GroupMemberInline(admin.TabularInline):
    """
    Inline configuration for displaying and managing GroupMember
    instances within the Group admin interface.

    This allows the admin to view and edit group members directly on the
    Group detail page in the Django admin.
    """

    model = GroupMember
    extra = 0  # Specifies the number of extra empty forms to display


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Group model.

    This class customizes the admin interface for the Group model,
    including the ability to manage related GroupMember instances
    inline within the Group detail page.
    """

    inlines = [GroupMemberInline]
