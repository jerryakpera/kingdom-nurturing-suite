"""
Views for the core application.
"""

from django.shortcuts import render

from .models import FAQ


def index(request):
    """
    Render the index page of the core application.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the index page.
    """
    context = {}

    return render(
        request=request,
        template_name="core/pages/index.html",
        context=context,
    )


def about_view(request):
    """
    Render the about page of the core application.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the about page.
    """
    context = {}

    return render(
        request=request,
        template_name="core/pages/about.html",
        context=context,
    )


def faqs_view(request):
    """
    Render the faqs page of the core application.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the faqs page.
    """

    faqs = FAQ.objects.all()

    context = {
        "faqs": faqs,
    }

    return render(
        request=request,
        template_name="core/pages/faqs.html",
        context=context,
    )


def submit_ticket_view(request):
    """
    Render the submit ticket page of the core application.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the submit ticket page.
    """
    context = {}

    return render(
        request=request,
        template_name="core/pages/submit_ticket.html",
        context=context,
    )
