"""
Django admin site configuration for the `movements` app.
"""

from django.contrib import admin

from .models import Movement, MovementSyllabusItem, MovementTopic, ProfileMovement


class MovementSyllabusItemInline(admin.TabularInline):
    """
    Inline admin for managing MovementSyllabusItem entries related to a Movement.
    """

    model = MovementSyllabusItem
    extra = 1
    verbose_name = "Syllabus Item"
    verbose_name_plural = "Syllabus Items"


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Movement entries.
    """

    list_display = (
        "title",
        "author",
        "prayer_movement",
        "created_at",
    )
    search_fields = ("title", "author__name")
    list_filter = ("prayer_movement", "created_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = [MovementSyllabusItemInline]


@admin.register(MovementTopic)
class MovementTopicAdmin(admin.ModelAdmin):
    """
    Admin interface for managing MovementTopic entries.
    """

    list_display = ("title", "author", "created_at")
    search_fields = ("title", "author__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProfileMovement)
class ProfileMovementAdmin(admin.ModelAdmin):
    """
    Admin interface for managing ProfileMovement entries.
    """

    list_display = (
        "profile",
        "movement",
        "comprehension",
        "created_at",
        "updated_at",
    )
    search_fields = ("profile__name", "movement__title")
    list_filter = ("comprehension", "created_at")
    readonly_fields = ("created_at", "updated_at")
