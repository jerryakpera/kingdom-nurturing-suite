"""
URLs for the `api` for the levels app.
"""

from django.urls import path

from . import api_views

urlpatterns = [
    path(
        route="levels/",
        view=api_views.levels_list,
        name="levels_list",
    ),
    path(
        route="levels/<int:id>",
        view=api_views.level_detail,
        name="level_detail",
    ),
    path(
        route="sublevels/",
        view=api_views.sublevels_list,
        name="sublevels_list",
    ),
]
