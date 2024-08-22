"""
Views for the core application.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from kns.groups.models import Group
from kns.profiles.models import Profile

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
    context = {
        "groups_count": Group.objects.all().count(),
        "members_count": Profile.objects.all().count(),
    }

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


def contact_view(request):
    """
    Render the contact page of the core application.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the contact page.
    """
    context = {}

    return render(
        request=request,
        template_name="core/pages/contact.html",
        context=context,
    )


# def error_500(request, *args, **argv):
#     return render(request, "500.html", status=500)


def error_404(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    """
    Render the error page of the core application.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    exception : Exception
        The exception that triggered the 404 error.

    Returns
    -------
    HttpResponse
        The rendered HTML response for the error page.
    """
    context = {}

    return render(
        request,
        "404.html",
        context,
        status=404,
    )
