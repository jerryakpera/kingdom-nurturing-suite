from django.urls import path

from . import views

app_name = "groups"

urlpatterns = [
    path(
        "new/",
        views.register_group,
        name="register_group",
    ),
    path(
        "<slug:group_slug>/",
        views.group_overview,
        name="group_overview",
    ),
    path(
        "<slug:group_slug>/members",
        views.group_members,
        name="group_members",
    ),
    path(
        "<slug:group_slug>/activities",
        views.group_activities,
        name="group_activities",
    ),
    path(
        "<slug:group_slug>/sub-groups",
        views.group_subgroups,
        name="group_subgroups",
    ),
    path(
        "",
        views.index,
        name="index",
    ),
]
