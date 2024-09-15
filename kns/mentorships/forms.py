"""
Forms for the `Mentorships` App.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from kns.core.models import Setting
from kns.mentorships.models import MentorshipArea


class ProfileMentorshipAreasForm(forms.Form):
    """
    A form for managing a profile's mentorship areas.
    This form allows users to select multiple mentorship areas in which
    the user is willing to provide training to others.

    Parameters
    ----------
    *args : tuple
        Variable length argument list passed to the parent class.
    **kwargs : dict
        Arbitrary keyword arguments passed to the parent class.

    Attributes
    ----------
    mentorship_areas : ModelMultipleChoiceField
        A multiple-choice field for selecting mentorship areas where the user
        is willing to provide training.
    """

    mentorship_areas = forms.ModelMultipleChoiceField(
        required=False,
        queryset=MentorshipArea.objects.filter(status="published"),
        help_text=(
            "Select the mentorship areas this user is willing and able "
            "to train others in. Hold Ctrl to select multiple mentorship areas"
        ),
        widget=forms.SelectMultiple(
            attrs={
                "id": "mentorship_areas",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with the available mentorship areas.

        Parameters
        ----------
        *args : tuple
            Variable length argument list passed to the parent class.
        **kwargs : dict
            Arbitrary keyword arguments passed to the parent class.
        """
        super().__init__(*args, **kwargs)
        self.fields["mentorship_areas"].queryset = MentorshipArea.objects.filter(
            status="published"
        )

    def clean(self):
        """
        Clean and validate the form data.

        This method checks that the selected mentorship areas do not exceed
        the allowed limit specified in the settings. If the number of selected
        mentorship areas exceeds the maximum allowed, an error is raised.

        Returns
        -------
        dict
            The cleaned form data.

        Raises
        ------
        ValidationError
            If the number of selected mentorship areas exceeds the allowed limit.
        """
        cleaned_data = super().clean()
        mentorship_areas = cleaned_data.get("mentorship_areas", [])

        settings = Setting.get_or_create_setting()

        # Ensure at least one mentorship area is selected
        if not mentorship_areas:
            self.add_error(
                "mentorship_areas", "At least one mentorship area is required."
            )

        # Check for the maximum limit of selected mentorship areas
        if len(mentorship_areas) > settings.max_mentorship_areas_per_user:
            error_msg = (
                "You can select up to "
                f"{settings.max_mentorship_areas_per_user} mentorship areas."
            )

            self.add_error("mentorship_areas", error_msg)

        return cleaned_data
