from django.urls import path

from . import views

app_name = "discipleships"

urlpatterns = [
    path(
        route="move/<str:new_group>/<int:discipleship_id>/",
        view=views.move_to_discipleship_group,
        name="move_to_discipleship_group",
    ),
    path(
        "<slug:profile_slug>/discipleships",
        views.profile_discipleships,
        name="profile_discipleships",
    ),
    path(
        "<slug:discipleship_slug>/",
        views.discipleship_history,
        name="discipleship_history",
    ),
    path(
        "",
        views.index,
        name="index",
    ),
]
