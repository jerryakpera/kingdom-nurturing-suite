"""
URL configuration for the `api` app.
"""

from django.urls import include, path

app_name = "apis"

urlpatterns = [
    path(
        "",
        include("kns.groups.api_urls"),
    ),
]
