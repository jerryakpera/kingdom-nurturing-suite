"""
Context processors for the `core` app.
"""

from .models import Setting


def settings_context(request):
    """
    Add settings to the context for all templates.

    Parameters
    ----------
    request : HttpRequest
        A HttpRequest object.

    Returns
    -------
    dict
        A dictionary with a 'settings' key containing the settings instance.
    """
    settings = Setting.get_or_create_setting()

    return {
        "settings": settings,
    }
