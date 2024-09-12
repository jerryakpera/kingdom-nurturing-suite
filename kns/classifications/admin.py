"""
Django admin site configuration for the `classifications` app.
"""

from django.contrib import admin

from .models import Classification, ClassificationSubclassification, Subclassification


class ClassificationSubclassificationInline(admin.TabularInline):
    """
    Inline admin interface for managing the many-to-many relationship
    between Classifications and Subclassifications.

    Attributes
    ----------
    model : ClassificationSubclassification
        The model associated with this inline.
    extra : int
        Number of empty forms to display.
    """

    model = ClassificationSubclassification
    extra = 0


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    """
    Admin interface for the Classification model. Provides configuration for the
    display, filtering, and inline editing of Classifications.

    Attributes
    ----------
    list_display : tuple
        Fields to display in the list view.
    inlines : list
        Inline model admins to display on the Classification admin page.
    readonly_fields : tuple
        Fields to make read-only.
    search_fields : tuple
        Fields to enable search functionality.
    list_filter : tuple
        Fields to enable filtering.
    """

    list_display = ("title", "author", "created_at")
    inlines = [ClassificationSubclassificationInline]
    readonly_fields = ("slug",)
    search_fields = ("title", "author__user__email")
    list_filter = ("author",)


@admin.register(Subclassification)
class SubclassificationAdmin(admin.ModelAdmin):
    """
    Admin interface for the Subclassification model. Provides configuration for
    the display, filtering, and management of Subclassifications.

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
