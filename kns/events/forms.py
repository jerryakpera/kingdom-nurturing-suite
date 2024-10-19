"""
Forms for the `events` app.
"""

from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator
from taggit.forms import TagField, TagWidget
from tinymce.widgets import TinyMCE

from . import constants as event_constants
from .models import Event


class EventContentForm(forms.ModelForm):
    """
    Form for creating or editing the content of an event.
    """

    class Meta:
        model = Event
        fields = ["title", "summary", "description", "tags"]

    title = forms.CharField(
        label="Event Title",
        help_text="Give your event a title.",
        validators=[
            MinLengthValidator(
                event_constants.EVENT_TITLE_MIN_LENGTH,
                message=(
                    "The title must be at least "
                    f"{event_constants.EVENT_TITLE_MIN_LENGTH} characters long"
                ),
            ),
            MaxLengthValidator(
                event_constants.EVENT_TITLE_MAX_LENGTH,
                message=(
                    "The title must be at most "
                    f"{event_constants.EVENT_TITLE_MAX_LENGTH} characters long"
                ),
            ),
        ],
        widget=forms.TextInput(
            attrs={
                "id": "title",
                "name": "title",
                "autofocus": True,
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
                "placeholder": "Give your event a suitable title",
            }
        ),
    )

    summary = forms.CharField(
        label="Event Summary",
        help_text="Summarize the event briefly.",
        widget=forms.Textarea(
            attrs={
                "id": "summary",
                "name": "summary",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
                "placeholder": "Write a summary of the event",
            }
        ),
        validators=[
            MinLengthValidator(
                event_constants.EVENT_SUMMARY_MIN_LENGTH,
                message=(
                    "The event summary must be at least "
                    f"{event_constants.EVENT_SUMMARY_MIN_LENGTH} characters long"
                ),
            ),
            MaxLengthValidator(
                event_constants.EVENT_SUMMARY_MAX_LENGTH,
                message=(
                    "The event summary must be no more than "
                    f"{event_constants.EVENT_SUMMARY_MAX_LENGTH} characters long"
                ),
            ),
        ],
    )

    description = forms.CharField(
        label="Event description",
        help_text="Provide a more detailed description of the event.",
        widget=TinyMCE(
            attrs={
                "id": "description",
                "name": "description",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
                "placeholder": "Write a comprehensive description of the event",
            }
        ),
    )

    tags = TagField(
        label="Event Tags",
        required=False,
        widget=TagWidget(
            attrs={
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                )
            }
        ),
        help_text="Separate tags using a comma",
    )

    def clean_tags(self):
        """
        Validate the tags field to ensure the event has no more than 5 tags.

        Returns
        -------
        list
            The validated list of tags.

        Raises
        ------
        forms.ValidationError
            If more than 5 tags are provided.
        """
        tags = self.cleaned_data.get("tags")

        if tags and len(tags) > event_constants.MAX_TAGS:
            raise forms.ValidationError(
                f"An event cannot have more than {event_constants.MAX_TAGS} tags.",
            )

        return tags
