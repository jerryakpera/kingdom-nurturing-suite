"""
Forms for the `classifications` app.
"""

from django import forms
from django.conf import settings

from .models import Classification, Subclassification


class ProfileClassificationForm(forms.Form):
    """
    A form for selecting a profile classification and an optional
    subclassification. This form allows users to choose from available
    classifications and subclassifications related to their profile.

    Attributes
    ----------
    classification : ModelChoiceField
        A dropdown field for selecting a classification from available
        classifications.
    subclassification : ModelChoiceField
        An optional dropdown field for selecting a subclassification,
        disabled by default.
    url : CharField
        A hidden field containing the API URL used to fetch
        subclassifications dynamically.
    """

    api_url = settings.API_URL if settings.DEBUG else settings.API_URL

    classification = forms.ModelChoiceField(
        queryset=Classification.objects.all(),
        widget=forms.Select(
            attrs={
                "id": "classification_select",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            },
        ),
    )

    subclassification = forms.ModelChoiceField(
        required=False,
        queryset=Subclassification.objects.all(),
        widget=forms.Select(
            attrs={
                "disabled": True,
                "id": "subclassification_select",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            }
        ),
    )

    url = forms.CharField(
        label="",
        required=False,
        widget=forms.HiddenInput(
            attrs={
                "id": "url_input",
                "data-url": api_url,
            }
        ),
    )
