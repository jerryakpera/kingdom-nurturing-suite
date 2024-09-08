"""
URL configuration for the groups API.

This module defines the URL patterns for the groups-related API views.
It routes HTTP requests to appropriate views in the `api_views` module.

URLs:
    - groups/<int:pk>/descendants/ : Fetches the descendants of a
    specified group.
"""

from django.urls import path

from . import api_views

urlpatterns = [
    path(
        "groups/<int:pk>/descendants/",
        api_views.group_descendants,
        name="group_descendants",
    ),
]
