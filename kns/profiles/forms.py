"""
Forms for the `profiles` app.
"""

from django import forms

from .models import Profile


class ProfileSettingsForm(forms.ModelForm):
    """
    A form for updating the visibility settings of a user's profile in the application.

    This form allows users to choose whether to display their date and place of birth
    as well as their contact details (phone, email, and location) on their profile.
    """

    bio_details_is_visible = forms.BooleanField(
        required=False,
        label="Display the date and place of birth of this profile",
        widget=forms.CheckboxInput(
            attrs={
                "class": (
                    "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 "
                    "rounded focus:ring-blue-500"
                )
            }
        ),
    )
    """
    A BooleanField for toggling the visibility of the user's date
    and place of birth on their profile.

    - `required`: Indicates that this field is not mandatory.
    - `label`: The label for the field displayed on the form.
    - `widget`: A CheckboxInput widget with custom classes for styling.
    """

    contact_details_is_visible = forms.BooleanField(
        required=False,
        label="Display the phone, email and location of this profile",
        widget=forms.CheckboxInput(
            attrs={
                "class": (
                    "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 "
                    "rounded focus:ring-blue-500"
                )
            }
        ),
    )
    """
    A BooleanField for toggling the visibility of the user's contact details on their profile.

    - `required`: Indicates that this field is not mandatory.
    - `label`: The label for the field displayed on the form.
    - `widget`: A CheckboxInput widget with custom classes for styling.
    """

    class Meta:
        model = Profile
        fields = [
            "bio_details_is_visible",
            "contact_details_is_visible",
        ]

    """
    Meta information for the ProfileSettingsForm.

    - `model`: Specifies that this form is associated with the Profile model.
    - `fields`: A list of fields to be included in the form, specifically
      `bio_details_is_visible` and `contact_details_is_visible`.
    """
