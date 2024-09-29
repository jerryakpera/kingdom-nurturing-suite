from django.urls import path

from . import views

app_name = "discipleships"

urlpatterns = [
    path(
        "<int:discipleship_id>/group-member/",
        views.move_to_group_member,
        name="move_to_group_member",
    ),
    path(
        "<int:discipleship_id>/first-12/",
        views.move_to_first_12,
        name="move_to_first_12",
    ),
    path(
        "<int:discipleship_id>/first-3/",
        views.move_to_first_3,
        name="move_to_first_3",
    ),
    path(
        "<int:discipleship_id>/send-forth/",
        views.move_to_sent_forth,
        name="move_to_sent_forth",
    ),
    path(
        "<slug:profile_slug>/discipleships",
        views.profile_discipleships,
        name="profile_discipleships",
    ),
]
