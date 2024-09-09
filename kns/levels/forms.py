"""
Forms for the `levels` app.
"""

from django import forms
from django.conf import settings

from .models import Level, Sublevel


class ProfileLevelForm(forms.Form):
    """
    A form for selecting a profile level and an optional sublevel.
    This form allows users to choose from available levels and sublevels
    related to their profile.

    Attributes
    ----------
    level : ModelChoiceField
        A dropdown field for selecting a level from available levels.
    sublevel : ModelChoiceField
        An optional dropdown field for selecting a sublevel, disabled by default.
    url : CharField
        A hidden field containing the API URL used to fetch sublevels dynamically.
    """

    api_url = settings.API_URL if settings.DEBUG else settings.API_URL

    level = forms.ModelChoiceField(
        queryset=Level.objects.all(),
        widget=forms.Select(
            attrs={
                "id": "level_select",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            },
        ),
    )

    sublevel = forms.ModelChoiceField(
        required=False,
        queryset=Sublevel.objects.all(),
        widget=forms.Select(
            attrs={
                "disabled": True,
                "id": "sublevel_select",
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
