from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path(
        "",
        views.index,
        name="index",
    ),
    path(
        "about",
        views.about_view,
        name="about",
    ),
    path(
        "faqs",
        views.faqs_view,
        name="faqs",
    ),
    path(
        "submit-ticket",
        views.submit_ticket_view,
        name="submit_ticket",
    ),
    path(
        "dismiss-getting-started",
        views.dismiss_getting_started,
        name="dismiss_getting_started",
    ),
    path(
        "notifications/read-redirect/<int:notification_id>/",
        views.mark_notification_and_redirect,
        name="mark_notification_and_redirect",
    ),
    path(
        "contact",
        views.contact_view,
        name="contact",
    ),
]
