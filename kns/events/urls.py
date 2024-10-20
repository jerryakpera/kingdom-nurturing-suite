"""
URLs for the `events` app.
"""

from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path(
        route="",
        view=views.index,
        name="index",
    ),
    path(
        route="create-event/",
        view=views.EventWizardView.as_view(),
        name="create_event",
    ),
    path(
        route="<slug:event_slug>/",
        view=views.event_detail,
        name="event_detail",
    ),
    path(
        route="<slug:event_slug>/activities",
        view=views.event_activities,
        name="event_activities",
    ),
]
