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
        "milestones/<int:milestone_id>/remove",
        views.remove_group_milestone,
        name="remove_group_milestone",
    ),
    path(
        "<slug:group_slug>/edit-milestones",
        views.edit_group_milestones,
        name="edit_group_milestones",
    ),
    path(
        "<slug:group_slug>/edit",
        views.edit_group,
        name="edit_group",
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
