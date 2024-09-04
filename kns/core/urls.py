from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    # http://localhost:8000/make-leader-action-approval/14/Mg/ccs9uj-faad510cb4121e6ccc12f039acc96d7f/approve/
    path(
        "make-leader-action-approval/<int:action_approval_id>/<uidb64>/<token>/approve/",
        views.approve_make_leader_action,
        name="approve_make_leader_action",
    ),
    path(
        "make-leader-action-approval/<int:action_approval_id>/<uidb64>/<token>/approve/",
        views.reject_make_leader_action,
        name="reject_make_leader_action",
    ),
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
