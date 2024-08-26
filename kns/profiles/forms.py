"""
Forms for the `profiles` app.
"""

from cloudinary.forms import CloudinaryFileField
from django import forms
from django.core.exceptions import ValidationError

from .models import ConsentForm, Profile


class ProfileSettingsForm(forms.ModelForm):
    """
    A form for updating the visibility settings of a user's profile in the application.

    This form allows users to choose whether to display their date and place of birth
    as well as their contact details (phone, email, and location) on their profile.
    """

    class Meta:
        model = Profile
        fields = [
            "bio_details_is_visible",
            "contact_details_is_visible",
        ]

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

    def clean(self):  # pragma: no cover
        cleaned_data = super().clean()
        bio_visibility = cleaned_data.get("bio_details_is_visible")
        contact_visibility = cleaned_data.get("contact_details_is_visible")

        if not isinstance(bio_visibility, bool):
            self.add_error(
                "bio_details_is_visible",
                "Invalid value for bio details visibility.",
            )

        if not isinstance(contact_visibility, bool):
            self.add_error(
                "contact_details_is_visible",
                "Invalid value for contact details visibility.",
            )

        return cleaned_data


class ConsentFormSubmission(forms.ModelForm):
    """
    A form for submitting a consent form.

    This form is based on the ConsentForm model and allows users to
    upload a consent form and submit it for review.

    Parameters
    ----------
    *args : tuple
        Positional arguments passed to the parent class.
    **kwargs : dict
        Keyword arguments passed to the parent class.
    """

    class Meta:
        model = ConsentForm
        fields = ["consent_form"]

    consent_form = CloudinaryFileField(
        required=True,
        options={
            "folder": "kns/files/consent_forms/",
        },
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form.

        Parameters
        ----------
        *args : tuple
            Positional arguments passed to the parent class.
        **kwargs : dict
            Keyword arguments passed to the parent class.
        """

        super().__init__(*args, **kwargs)

        self.fields["consent_form"].label = "Upload Consent Form"

    def clean_consent_form(self):  # pragma: no cover
        """
        Validate the uploaded consent form file to ensure it has
        a valid extension.

        Returns
        -------
        file
            The validated consent form file.

        Raises
        ------
        ValidationError
            If the file format is not in the allowed formats.
        """

        file = self.cleaned_data.get("consent_form")

        if file:
            extension = file.format
            valid_extensions = ["pdf", "jpg", "jpeg", "png"]

            if extension not in valid_extensions:
                raise ValidationError(
                    "The consent form must be a PDF, JPG, or PNG file."
                )

        return file
