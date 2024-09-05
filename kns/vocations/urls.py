"""
URLs for the `vocations` app.
"""

from django.urls import path

from . import views

app_name = "vocations"


urlpatterns = [
    path(
        route="",
        view=views.index,
        name="index",
    ),
    path(
        route="<int:vocation_id>",
        view=views.vocation_detail,
        name="vocation_detail",
    ),
]
