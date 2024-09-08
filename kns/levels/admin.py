"""
Django admin site configuration for the `levels` app.
"""

from django.contrib import admin

from .models import Level, LevelSublevel, Sublevel


class LevelSublevelInline(admin.TabularInline):
    """
    Inline admin interface for managing the many-to-many relationship
    between Levels and Sublevels.

    Attributes
    ----------
    model : LevelSublevel
        The model associated with this inline.
    extra : int
        Number of empty forms to display.
    """

    model = LevelSublevel
    extra = 0


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """
    Admin interface for the Level model. Provides configuration for the
    display, filtering, and inline editing of Levels.

    Attributes
    ----------
    list_display : tuple
        Fields to display in the list view.
    inlines : list
        Inline model admins to display on the Level admin page.
    readonly_fields : tuple
        Fields to make read-only.
    search_fields : tuple
        Fields to enable search functionality.
    list_filter : tuple
        Fields to enable filtering.
    """

    list_display = ("title", "author", "created_at")
    inlines = [LevelSublevelInline]
    readonly_fields = ("slug",)
    search_fields = ("title", "author__user__email")
    list_filter = ("author",)


@admin.register(Sublevel)
class SublevelAdmin(admin.ModelAdmin):
    """
    Admin interface for the Sublevel model. Provides configuration for
    the display, filtering, and management of Sublevels.

    Attributes
    ----------
    list_display : tuple
        Fields to display in the list view.
    readonly_fields : tuple
        Fields to make read-only.
    search_fields : tuple
        Fields to enable search functionality.
    list_filter : tuple
        Fields to enable filtering.
    """

    list_display = ("title", "author", "created_at")
    readonly_fields = ("slug",)
    search_fields = ("title", "author__user__email")
    list_filter = ("author",)
