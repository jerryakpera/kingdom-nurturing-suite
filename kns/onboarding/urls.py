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
]  # pragma: no cover
