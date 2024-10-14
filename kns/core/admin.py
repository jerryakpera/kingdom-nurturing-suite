"""
Django admin site configuration for the core app.
"""

from django.contrib import admin

from .models import FAQ, Notification, NotificationRecipient, Setting

# Registering the FAQ model with the admin site
admin.site.register(FAQ)

# Registering the Setting model with the admin site
admin.site.register(Setting)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Notification model.

    This class customizes the admin interface for the Notification model,
    including the ability to filter and search notifications.
    """

    list_display = (
        "id",
        "notification_type",
        "sender",
        "created_at",
    )
    search_fields = (
        "notification_type",
        "message",
        "sender__user__username",
    )
    list_filter = ("notification_type", "created_at")


@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(admin.ModelAdmin):
    """
    Admin configuration for the NotificationRecipient model.

    This class customizes the admin interface for the NotificationRecipient model,
    allowing management of recipients for notifications, including filtering and searching.
    """

    list_display = (
        "id",
        "notification",
        "recipient",
        "is_read",
        "read_at",
    )
    search_fields = (
        "notification__message",
        "recipient__user__username",
    )
    list_filter = ("is_read", "read_at")
