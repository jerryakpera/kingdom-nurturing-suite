"""
Forms for the `events` app.
"""

from django import forms
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.utils import timezone
from django_countries.widgets import CountrySelectWidget
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


class EventDatesForm(forms.ModelForm):
    """
    Form for setting the dates and deadlines of an event.
    """

    class Meta:
        model = Event
        fields = [
            "start_date",
            "end_date",
            "registration_deadline_date",
        ]

    start_date = forms.DateField(
        help_text="Please select the date when the event starts.",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "id": "start_date",
                "name": "start_date",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
                "placeholder": "Select start date",
            }
        ),
    )

    end_date = forms.DateField(
        help_text="Please select the date when the event will end.",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "id": "end_date",
                "disabled": True,
                "name": "end_date",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
                "placeholder": "Select end date (optional)",
            }
        ),
        required=False,
    )

    registration_deadline_date = forms.DateField(
        help_text="Please select the last date for registering for this event.",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "disabled": True,
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
                "id": "registration_deadline_date",
                "name": "registration_deadline_date",
                "placeholder": "Select registration deadline date",
            }
        ),
        required=True,
    )

    def clean_start_date(self):
        """
        Validate the start date to ensure it is at least 3 days in the future.

        Returns
        -------
        date
            The validated start date.

        Raises
        ------
        forms.ValidationError
            If the start date is not at least 3 days in the future.
        """
        start_date = self.cleaned_data.get("start_date")

        if start_date < timezone.now().date() + timezone.timedelta(
            days=event_constants.EVENT_MIN_DAYS_IN_FUTURE
        ):
            raise forms.ValidationError(event_constants.ERROR_START_DATE_FUTURE)

        return start_date

    def clean_end_date(self):
        """
        Validate the end date to ensure it is not before the start date.

        Returns
        -------
        date
            The validated end date.

        Raises
        ------
        forms.ValidationError
            If the end date is before the start date.
        """
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")

        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError(event_constants.ERROR_END_DATE)

        return end_date

    def clean_registration_deadline_date(self):
        """
        Validate the registration deadline date to ensure it is before the start date.

        Returns
        -------
        date
            The validated registration deadline date.

        Raises
        ------
        forms.ValidationError
            If the registration deadline date is not before the event start date.
        """
        start_date = self.cleaned_data.get("start_date")
        registration_deadline_date = self.cleaned_data.get("registration_deadline_date")

        if (
            registration_deadline_date
            and start_date
            and registration_deadline_date >= start_date
        ):
            raise forms.ValidationError(event_constants.ERROR_REGISTRATION_DEADLINE)

        return registration_deadline_date


class EventLocationForm(forms.ModelForm):
    """
    Form for selecting the location of an event.
    """

    class Meta:
        model = Event
        fields = [
            "location_country",
            "location_city",
        ]
        widgets = {
            "location_country": CountrySelectWidget(
                attrs={
                    "id": "location_country",
                    "name": "location_country",
                    "class": "form-select input-field",
                    "placeholder": "Select country",
                    "autocomplete": "off",
                }
            ),
            "location_city": forms.TextInput(
                attrs={
                    "id": "location_city",
                    "name": "location_city",
                    "autocomplete": "off",
                    "class": "form-control input-field",
                    "placeholder": "Enter city",
                }
            ),
        }
        labels = {
            "location_country": "Country",
            "location_city": "City",
        }
        help_texts = {
            "location_country": event_constants.HELP_TEXT_COUNTRY,
            "location_city": event_constants.HELP_TEXT_CITY,
        }
        required = {
            "location_country": True,
            "location_city": True,
        }

    def clean(self):
        """
        Validate that both city and country fields are filled if one is provided.
        """
        cleaned_data = super().clean()
        location_country = cleaned_data.get("location_country")
        location_city = cleaned_data.get("location_city")

        # Check if both fields are empty and raise field-specific error
        if not location_country and not location_city:
            self.add_error(
                "location_country",
                event_constants.ERROR_NO_COUNTRY_AND_CITY,
            )
            self.add_error(
                "location_city",
                event_constants.ERROR_NO_COUNTRY_AND_CITY,
            )

        if location_city and not location_country:
            self.add_error(
                "location_country",
                event_constants.ERROR_NO_LOCATION_COUNTRY,
            )

        if location_country and not location_city:
            self.add_error(
                "location_city",
                event_constants.ERROR_NO_LOCATION_CITY,
            )

        return cleaned_data


class EventMiscForm(forms.ModelForm):
    """
    Form for managing miscellaneous event settings such as refreshments, accommodation,
    and registration limits.
    """

    class Meta:
        model = Event
        fields = ["refreshments", "accommodation", "registration_limit"]

    refreshments = forms.BooleanField(
        label="Provide Refreshments",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    accommodation = forms.BooleanField(
        label="Provide Accommodation",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    registration_limit = forms.IntegerField(
        label="Registration Limit",
        initial=event_constants.EVENT_DEFAULT_REGISTRATION_LIMIT,
        required=True,
        validators=[
            MinValueValidator(
                1,
                message=event_constants.REGISTRATION_LIMIT_ERROR_MESSAGE,
            )
        ],
        widget=forms.NumberInput(
            attrs={
                "class": "form-control input-field",
                "min": "1",
                "placeholder": "Enter registration limit",
            }
        ),
    )
