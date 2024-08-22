from django.urls import path

from . import views

app_name = "profiles"

urlpatterns = [
    path(
        "<slug:profile_slug>/activities",
        views.profile_activities,
        name="profile_activities",
    ),
    path(
        "<slug:profile_slug>/settings",
        views.profile_settings,
        name="profile_settings",
    ),
    path(
        "<slug:profile_slug>/trainings",
        views.profile_trainings,
        name="profile_trainings",
    ),
    path(
        "<slug:profile_slug>/involvements",
        views.profile_involvements,
        name="profile_involvements",
    ),
    path(
        "<slug:profile_slug>/",
        views.profile_detail,
        name="profile_detail",
    ),
    path(
        "",
        views.index,
        name="index",
    ),
]
