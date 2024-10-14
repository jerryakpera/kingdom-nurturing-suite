"""
Django admin configuration for the `groups` app.
"""

from django.contrib import admin

from kns.faith_milestones.models import FaithMilestone, GroupFaithMilestone

from .models import Group, GroupMember


class GroupFaithMilestoneInline(admin.TabularInline):
    """
    Inline admin interface for the GroupFaithMilestone model.

    This allows the interests associated with a profile to be managed
    directly within the Group admin interface.
    """

    extra = 0
    model = GroupFaithMilestone

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filter the faith milestone choices to only include those of type 'group'.

        Parameters
        ----------
        db_field : models.Field
            The model field for which the foreign key relation is being defined.
        request : HttpRequest
            The current request object.
        **kwargs
            Additional keyword arguments.

        Returns
        -------
        models.Field
            The filtered model field.
        """
        if db_field.name == "faith_milestone":
            kwargs["queryset"] = FaithMilestone.objects.filter(
                type="group",
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )


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

    inlines = [
        GroupMemberInline,
        GroupFaithMilestoneInline,
    ]

    # Customize the columns displayed in the Group list
    list_display = ["name", "leaders_full_name", "parent_group_name"]

    # Define a method to display the leader's full name
    def leaders_full_name(self, obj):
        """
        Retrieve the full name of the leader of the group.

        Parameters
        ----------
        obj : Group
            The Group instance for which the leader's name is retrieved.

        Returns
        -------
        str
            The full name of the group's leader.
        """
        return obj.leader.get_full_name()

    leaders_full_name.short_description = "Leader"

    # Define a method to display the parent group's name
    def parent_group_name(self, obj):
        """
        Retrieve the name of the parent group.

        If the group does not have a parent, it returns a placeholder.

        Parameters
        ----------
        obj : Group
            The Group instance for which the parent group's name is retrieved.

        Returns
        -------
        str
            The name of the parent group if it exists; otherwise, a placeholder.
        """
        if obj.parent:
            return obj.parent.name
        return "---"

    parent_group_name.short_description = "Parent Group"
