"""
Forms for the `skills` app.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from kns.core.models import Setting
from kns.skills.models import Skill


class ProfileSkillsForm(forms.Form):
    """
    A form for editing a user's profile skills and interests.
    This form allows users to select multiple skills they are willing to train others in
    and multiple interests they are keen on learning.

    Parameters
    ----------
    *args : tuple
        Variable length argument list passed to the parent class.
    **kwargs : dict
        Arbitrary keyword arguments passed to the parent class.

    Attributes
    ----------
    skills : ModelMultipleChoiceField
        A multiple-choice field for selecting skills.
    interests : ModelMultipleChoiceField
        A multiple-choice field for selecting interests.
    """

    skills = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Skill.objects.all(),
        help_text=(
            "Select the skills this user is willing and "
            "able to train others in. Hold Ctrl to select multiple skills."
        ),
        widget=forms.SelectMultiple(
            attrs={
                "id": "skills",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            }
        ),
    )

    interests = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Skill.objects.all(),
        help_text=(
            "Select the skills this user is interested in "
            "learning. Hold Ctrl to select multiple interests."
        ),
        widget=forms.SelectMultiple(
            attrs={
                "id": "interests",
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
        Initialize the form with the available skills and interests.

        Parameters
        ----------
        *args : tuple
            Variable length argument list passed to the parent class.
        **kwargs : dict
            Arbitrary keyword arguments passed to the parent class.
        """
        super().__init__(*args, **kwargs)
        self.fields["skills"].queryset = Skill.objects.all()
        self.fields["interests"].queryset = Skill.objects.all()

    def clean(self):
        """
        Clean and validate the form data. Ensures no overlap between skills and interests,
        and that the number of selected skills and interests do not exceed allowed maximums.

        Returns
        -------
        dict
            The cleaned form data.

        Raises
        ------
        ValidationError
            If there is an overlap between selected skills and interests,
            or if the number of selected skills/interests exceeds the allowed maximum.
        """
        cleaned_data = super().clean()
        skills = cleaned_data.get("skills", [])
        interests = cleaned_data.get("interests", [])

        settings = Setting.get_or_create_setting()

        if len(skills) > settings.max_skills_per_user:
            error_msg = f"You can select up to {settings.max_skills_per_user} skills."
            self.add_error("skills", error_msg)

        if len(interests) > settings.max_interests_per_user:
            error_msg = (
                f"You can select up to {settings.max_interests_per_user} interests."
            )
            self.add_error("interests", error_msg)

        # Check for overlapping skills and interests
        overlapping_items = set(skills).intersection(interests)
        if overlapping_items:
            overlap_names = ", ".join([str(item) for item in overlapping_items])
            error_msg = (
                "The following items cannot be selected as both skills "
                f"and interests: {overlap_names}."
            )
            self.add_error("skills", error_msg)
            self.add_error("interests", error_msg)

        return cleaned_data
