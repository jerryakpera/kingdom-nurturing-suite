"""
URL configuration for the `api` app.
"""

from django.urls import include, path

app_name = "api"

urlpatterns = [
    path(
        "",
        include("kns.groups.api_urls"),
    ),
    path(
        "",
        include("kns.levels.api_urls"),
    ),
    path(
        "",
        include("kns.classifications.api_urls"),
    ),
]
