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
