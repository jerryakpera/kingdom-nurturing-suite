"""
URLs for the `onboarding` app.
"""

from django.urls import path

from . import views

app_name = "onboarding"

urlpatterns = [
    path(
        route="",
        view=views.index,
        name="index",
    ),
    path(
        route="back/",
        view=views.back,
        name="back",
    ),
    path(
        route="involvement",
        view=views.involvement,
        name="involvement",
    ),
    path(
        route="involvement",
        view=views.involvement,
        name="involvement",
    ),
    path(
        route="group",
        view=views.group,
        name="group",
    ),
    path(
        route="agree",
        view=views.agree,
        name="agree",
    ),
]
