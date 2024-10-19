"""
Django admin site configuration for the `events` app.
"""

from django.contrib import admin

from .models import Event, EventImage


class EventImageInline(admin.TabularInline):
    """
    Inline admin for EventImage to allow adding images directly in the Event admin page.
    """

    model = EventImage
    extra = 1  # Number of empty forms to display
    fields = ("image", "caption", "primary")
    readonly_fields = ("primary",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin interface for the Event model.
    """

    list_display = (
        "title",
        "start_date",
        "end_date",
        "registration_deadline_date",
        "author",
        "status",
    )
    search_fields = ("title", "summary", "description")
    list_filter = ("start_date", "end_date", "author", "status")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        EventImageInline,
    ]

    def save_model(self, request, obj, form, change):
        """
        Override the save_model method to customize saving the Event instance.

        Parameters
        ----------
        request : HttpRequest
            The current request object, which contains metadata about the request.
        obj : Event
            The event object being saved.
        form : ModelForm
            The form used to input and validate the data for the object.
        change : bool
            True if the object is being changed (updated); False if it's being added.
        """

        super().save_model(request, obj, form, change)
