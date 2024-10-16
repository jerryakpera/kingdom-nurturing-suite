"""
Django admin site configuration for the `movements` app.
"""

from django.contrib import admin

from .models import Movement, MovementTopic, ProfileMovement


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
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(MovementTopic)
class MovementTopicAdmin(admin.ModelAdmin):
    """
    Admin interface for managing MovementTopic entries.
    """

    list_display = ("title", "author", "created_at")
    search_fields = ("title", "author__name")
    prepopulated_fields = {"slug": ("title",)}
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
