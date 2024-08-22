"""
Utility functions for the `profiles` app.
"""

from django.urls import resolve


def get_profile_slug(request):
    """
    Extract the profile slug from the given HTTP request.

    This utility function is used to retrieve the slug of a profile from the
    URL path of the request. It specifically checks if the request path starts
    with "/profiles/" and, if so, resolves the path to extract the slug.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object from which to extract the profile slug.

    Returns
    -------
    str
        The profile slug if found, otherwise an empty string.
    """
    slug = ""

    if request.path.startswith("/profiles/"):
        match = resolve(request.path_info)
        # Extract the slug from the request path
        slug = match.kwargs.get("profile_slug")

    return slug
