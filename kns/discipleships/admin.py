"""
Django admin site configuration for the core app.
"""

from django.contrib import admin

from .models import Discipleship


@admin.register(Discipleship)
class DiscipleshipAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Discipleship model.
    Displays relevant fields in the admin list view.
    """

    list_display = (
        "discipler_name",
        "disciple_name",
        "group",
        "completed_at",
    )

    # Adding search functionality for easier navigation
    search_fields = (
        "disciple__first_name",
        "disciple__last_name",
        "discipler__first_name",
        "discipler__last_name",
    )

    def disciple_name(self, obj):
        """
        Return the full name of the disciple associated with the given Discipleship object.

        Parameters
        ----------
        obj : Discipleship
            The Discipleship instance for which the disciple's name is being retrieved.

        Returns
        -------
        str
            The full name of the disciple.
        """
        return f"{obj.disciple.get_full_name()}"

    def discipler_name(self, obj):
        """
        Return the full name of the discipler associated with the given Discipleship object.

        Parameters
        ----------
        obj : Discipleship
            The Discipleship instance for which the discipler's name is being retrieved.

        Returns
        -------
        str
            The full name of the discipler.
        """
        return f"{obj.discipler.get_full_name()}"

    discipler_name.short_description = "Discipler"
