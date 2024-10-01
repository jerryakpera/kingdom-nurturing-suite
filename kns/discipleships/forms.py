"""
Forms for the `profiles` app.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from kns.discipleships.models import Discipleship
from kns.profiles.models import Profile


class GroupMemberDiscipleForm(forms.ModelForm):
    """
    A form for selecting a disciple for a discipleship relationship
    within a group led by the current profile.

    Parameters
    ----------
    *args
        Variable length argument list.
    **kwargs
        Arbitrary keyword arguments.
    """

    class Meta:
        model = Discipleship
        fields = ["disciple"]

    disciple = forms.ModelChoiceField(
        required=True,
        queryset=Profile.objects.none(),
        label=(
            "Select a person in your group to add to your Group "
            "members discipleship group"
        ),
        widget=forms.Select(
            attrs={
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and filter the 'disciple' field's queryset
        based on the profile's group members.

        Parameters:
        -----------
        profile : Profile
            The profile leading the group, used to filter potential disciples.
        *args
            Variable length argument list.
        **kwargs
            Arbitrary keyword arguments.
        """

        profile = kwargs.pop("profile", None)
        super(GroupMemberDiscipleForm, self).__init__(*args, **kwargs)

        if profile:
            self.fields["disciple"].queryset = Profile.objects.filter(
                group_in__in=profile.group_led.members.all(),
                user__verified=True,
                user__agreed_to_terms=True,
            )


class DiscipleshipFilterForm(forms.Form):
    """
    A form for filtering discipleship groups.
    """

    filter_group = forms.ChoiceField(
        required=False,
        label="Filter Discipleship Group",
        choices=[
            ("", "----------"),
            ("group_member", "Group member"),
            ("first_12", "First 12"),
            ("first_3", "First 3"),
            ("sent_forth", "Sent forth"),
        ],
        widget=forms.Select(
            attrs={
                "id": "filter_group",
                "name": "filter_group",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-blue-500 focus:border-blue-500 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    filter_status = forms.ChoiceField(
        required=False,
        label="Filter Discipleship Status",
        choices=[
            ("", "----------"),
            ("all", "All"),
            ("ongoing", "Ongoing"),
            ("completed", "Completed"),
        ],
        widget=forms.Select(
            attrs={
                "id": "filter_status",
                "name": "filter_status",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-blue-500 focus:border-blue-500 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )
