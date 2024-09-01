"""
Forms for the `FaithMilestones` App.
"""

from django import forms

from .models import FaithMilestone


class ProfileFaithMilestonesForm(forms.Form):
    """
    A form for managing a profile's faith milestones.
    This form allows users to select multiple faith milestones that
    have been achieved by a profile.

    Parameters
    ----------
    *args : tuple
        Variable length argument list passed to the parent class.
    **kwargs : dict
        Arbitrary keyword arguments passed to the parent class.

    Attributes
    ----------
    faith_milestones : ModelMultipleChoiceField
        A multiple-choice field for selecting faith milestones.
    """

    faith_milestones = forms.ModelMultipleChoiceField(
        required=False,
        queryset=FaithMilestone.objects.filter(type="profile"),
        help_text=(
            "Select the faith milestones that have been achieved by this profile. "
            "Hold Ctrl to select multiple milestones."
        ),
        widget=forms.SelectMultiple(
            attrs={
                "id": "faith_milestones",
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
        Initialize the form with the available faith milestones.

        Parameters
        ----------
        *args : tuple
            Variable length argument list passed to the parent class.
        **kwargs : dict
            Arbitrary keyword arguments passed to the parent class.
        """
        super().__init__(*args, **kwargs)
        self.fields["faith_milestones"].queryset = FaithMilestone.objects.filter(
            type="profile",
        )


class GroupFaithMilestonesForm(forms.Form):
    """
    A form for managing a group's faith milestones.
    This form allows users to select multiple faith milestones that
    have been achieved by a group.

    Parameters
    ----------
    *args : tuple
        Variable length argument list passed to the parent class.
    **kwargs : dict
        Arbitrary keyword arguments passed to the parent class.

    Attributes
    ----------
    faith_milestones : ModelMultipleChoiceField
        A multiple-choice field for selecting faith milestones.
    """

    faith_milestones = forms.ModelMultipleChoiceField(
        required=False,
        queryset=FaithMilestone.objects.filter(type="group"),
        help_text=(
            "Select the faith milestones that have been achieved by this group. "
            "Hold Ctrl to select multiple milestones."
        ),
        widget=forms.SelectMultiple(
            attrs={
                "id": "faith_milestones",
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
        Initialize the form with the available faith milestones.

        Parameters
        ----------
        *args : tuple
            Variable length argument list passed to the parent class.
        **kwargs : dict
            Arbitrary keyword arguments passed to the parent class.
        """
        super().__init__(*args, **kwargs)

        self.fields["faith_milestones"].queryset = FaithMilestone.objects.filter(
            type="group",
        )
