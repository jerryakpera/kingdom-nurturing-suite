"""
URLs for the `api` for the classifications app.
"""

from django.urls import path

from . import api_views

urlpatterns = [
    path(
        route="classifications/",
        view=api_views.classifications_list,
        name="classifications_list",
    ),
    path(
        route="classifications/<int:id>",
        view=api_views.classification_detail,
        name="classification_detail",
    ),
    path(
        route="subclassifications/",
        view=api_views.subclassifications_list,
        name="subclassifications_list",
    ),
]
