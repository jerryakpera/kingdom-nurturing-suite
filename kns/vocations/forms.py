"""
Forms for the `vocations` app.
"""

from django import forms

from .models import Vocation


class ProfileVocationForm(forms.Form):
    """
    A form for selecting a vocation for a profile.

    This form allows users to choose from available vocations in the system.
    It utilizes a dropdown (select) widget for vocation selection.
    """

    vocations = forms.ModelMultipleChoiceField(
        label="Select vocations",
        queryset=Vocation.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                "id": "vocation_select",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            },
        ),
    )
