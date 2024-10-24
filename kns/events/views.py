"""
Views for the `events` application.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView

from kns.events.forms import (
    EventContactForm,
    EventContentForm,
    EventDatesForm,
    EventLocationForm,
    EventMiscForm,
)

from .constants import stepper_steps
from .models import Event
from .permissions import has_event_creation_permission


def index(request):
    """
    Render the index page for events.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the events index page, containing
        all events.
    """
    events = Event.objects.all().order_by("start_date")

    context = {
        "events": events,
    }

    return render(
        request=request,
        context=context,
        template_name="events/pages/index.html",
    )


class EventWizardView(LoginRequiredMixin, SessionWizardView):  # pragma: no cover
    """
    View for creating a new event using a multi-step wizard form.

    Inherits from SessionWizardView and requires the user to be logged in.

    Attributes
    ----------
    form_list : list
        A list of form classes used in the wizard.
    template_name : str
        The template to render the wizard.
    success_url : str
        URL to redirect to upon successful completion of the wizard.

    Methods
    -------
    get_context_data(**kwargs)
        Adds stepper information to the context for rendering.

    dispatch(request, *args, **kwargs)
        Checks if the user has permission to create an event before proceeding.

    done(form_list, **kwargs)
        Handles the final step of the wizard, creating and saving the event.
    """

    form_list = [
        EventContentForm,
        EventDatesForm,
        EventLocationForm,
        EventMiscForm,
        EventContactForm,
    ]
    template_name = "events/pages/create_event.html"
    success_url = reverse_lazy("events:index")

    def get_context_data(self, **kwargs):
        """
        Add stepper steps and current step information to the context.

        Parameters
        ----------
        **kwargs : keyword arguments
            Additional context parameters.

        Returns
        -------
        dict
            Updated context including stepper information.
        """
        # Get the existing context
        context = super().get_context_data(**kwargs)

        # Get the current step and relevant step info
        current_step_index = int(self.steps.current)
        current_step_info = stepper_steps[current_step_index]

        # Add the stepper steps and current step info to the context
        context.update(
            {
                "stepper_steps": stepper_steps,
                "current_step_info": current_step_info,
            }
        )

        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Check if the user has permission to create an event before processing
        the request.

        Parameters
        ----------
        request : django.http.HttpRequest
            The HTTP request object.
        *args : positional arguments
            Additional positional arguments.
        **kwargs : keyword arguments
            Additional keyword arguments.

        Returns
        -------
        django.http.HttpResponse
            Redirects to the events index if permission is denied,
            otherwise processes the request normally.
        """
        # Check if the user has permission to create an event
        if not has_event_creation_permission(request.user):
            messages.error(
                request,
                (
                    "You do not have permission to create an event. You must "
                    "verify your email address and register your group before "
                    "scheduling an event."
                ),
            )

            return redirect("events:index")

        return super().dispatch(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        """
        Handle the final step of the wizard, creating and saving the new event.

        Parameters
        ----------
        form_list : list
            List of form instances from the wizard.
        **kwargs : keyword arguments
            Additional context parameters.

        Returns
        -------
        django.http.HttpResponse
            Redirects to the newly created event detail page or back to
            the event creation page in case of an error.
        """
        content_form = form_list[0]
        dates_form = form_list[1]
        location_form = form_list[2]
        misc_form = form_list[3]
        contact_form = form_list[4]

        new_event = Event(
            title=content_form.cleaned_data.get("title"),
            summary=content_form.cleaned_data.get("summary"),
            description=content_form.cleaned_data.get("description"),
            start_date=dates_form.cleaned_data.get("start_date"),
            end_date=dates_form.cleaned_data.get("end_date"),
            location_country=location_form.cleaned_data.get("location_country"),
            location_city=location_form.cleaned_data.get("location_city"),
            event_contact_name=contact_form.cleaned_data.get("event_contact_name"),
            event_contact_email=contact_form.cleaned_data.get("event_contact_email"),
            refreshments=misc_form.cleaned_data.get("refreshments", False),
            accommodation=misc_form.cleaned_data.get("accommodation", False),
            author=self.request.user.profile,
        )

        try:
            # Save the new_event instance to the database first
            new_event.save()

            # Now that the event is saved, you can set the tags
            tags = content_form.cleaned_data.get("tags")
            if tags:
                new_event.tags.set(tags)

            messages.success(
                self.request,
                (
                    "Congratulations, your event has been created. Please "
                    "follow the instructions below to publish it."
                ),
            )

            return redirect(new_event)

        except ValidationError as e:
            messages.error(
                self.request,
                f"Error creating event: {e}",
            )

            return redirect("events:create_event")


def event_detail(request, event_slug):
    """
    Render the detail page for a specific event.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.
    event_slug : str
        The slug of the event to retrieve.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the event detail page.
    """
    context = {}

    return render(
        request=request,
        template_name="events/pages/event_detail.html",
        context=context,
    )


def event_activities(request, event_slug):
    """
    Render the activities page for a specific event.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.
    event_slug : str
        The slug of the event to retrieve.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the event activities page.
    """
    event = get_object_or_404(Event, slug=event_slug)
    event.request = request

    context = {
        "event": event,
    }

    return render(
        request=request,
        template_name="events/pages/event_activities.html",
        context=context,
    )
