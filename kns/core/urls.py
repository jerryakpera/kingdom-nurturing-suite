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
        "contact",
        views.contact_view,
        name="contact",
    ),
]
