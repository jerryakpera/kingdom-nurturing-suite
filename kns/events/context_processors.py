"""
Context processors for the `events` app.
"""

from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Event


def event_context(request):
    """
    Context processor to add the event and event form to the context.

    This context processor attempts to retrieve an event based on the slug obtained
    from the request. If the event exists, it also provides a form for editing
    the event.

    Parameters
    ----------
    request : HttpRequest
        A Http Request.

    Returns
    -------
    event : Event
        Event instance or None if not found.
    event_form : Form
        Form for editing the event, or None if the event is not found.
    """

    event = None
    can_edit_event = False
    event_slug = (
        request.resolver_match.kwargs.get("event_slug")
        if request.resolver_match
        else None
    )

    if event_slug:
        try:
            event = get_object_or_404(Event, slug=event_slug)

            if request.user and request.user.is_authenticated:
                can_edit_event = event.can_edit_event(request.user.profile)
        except Http404:
            # If the event is not found, event will remain None
            event = None

    return {
        "event": event,
        "can_edit_event": can_edit_event,
    }
