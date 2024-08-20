from django.urls import path

from . import views

app_name = "profiles"

urlpatterns = [
    path(
        "<slug:profile_slug>/",
        views.profile_detail,
        name="profile_detail",
    ),
    path(
        "create-profile",
        views.create_profile,
        name="create_profile",
    ),
    path(
        "",
        views.index,
        name="index",
    ),
]
