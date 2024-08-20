"""
Context processors for the `profiles` app.
"""

from .models import Profile


def user_profile_context(request):
    """
    Context processor to add the current user's profile to the context.

    Parameters
    ----------
    request : HttpRequest
        The request object.

    Returns
    -------
    dict
        A dictionary containing the current user's profile.
    """

    context = {}

    if request.user.is_authenticated:
        try:
            context["my_profile"] = request.user.profile
        except Profile.DoesNotExist:
            pass

    return context
