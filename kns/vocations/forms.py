"""
Forms for the `vocations` app.
"""

from django import forms

from .models import ProfileVocation, Vocation


class ProfileVocationForm(forms.Form):
    """
    A form for selecting a vocation for a profile.

    This form allows users to choose from available vocations in the system.
    It utilizes a dropdown (select) widget for vocation selection.
    """

    class Meta:
        """
        Meta information for the ProfileVocationForm.

        - model: Specifies the `ProfileVocation` model associated with
        this form.
        - fields: Specifies the fields to include in the form,
        specifically 'vocation'.
        """

        model = ProfileVocation
        fields = ["vocation"]

    vocation = forms.ModelChoiceField(
        label="Select vocation",
        queryset=Vocation.objects.all(),
        widget=forms.Select(
            attrs={
                "id": "vocation_select",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            },
        ),
    )
    """
    A ModelChoiceField for selecting a vocation from the available options.

    - label: The label for the field displayed as "Select vocation".
    - queryset: Provides the list of vocations from the `Vocation`
    model for the dropdown.
    - widget: A `Select` widget with attributes for custom styling and an ID.
    """
