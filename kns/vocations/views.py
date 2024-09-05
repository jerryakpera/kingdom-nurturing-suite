"""
Views for the `vocations` app.
"""

from django.shortcuts import get_object_or_404, render

from .models import Vocation


def index(request):
    """
    Render the index page for the vocations app.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        The rendered index page with an empty context.
    """
    context = {}

    return render(
        request=request,
        template_name="vocations/pages/index.html",
        context=context,
    )


def vocation_detail(request, vocation_id):
    """
    Render the detail page for a specific vocation.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    vocation_id : int
        The ID of the vocation to retrieve.

    Returns
    -------
    HttpResponse
        The rendered vocation detail page with the vocation object in the context.
    """
    vocation = get_object_or_404(Vocation, id=vocation_id)

    context = {
        "vocation": vocation,
    }

    return render(
        request=request,
        template_name="vocations/pages/vocation_detail.html",
        context=context,
    )
