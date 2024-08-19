"""
Forms for `groups`.
"""

from cloudinary.forms import CloudinaryFileField
from django import forms
from django_countries.fields import CountryField

from .models import Group


class GroupForm(forms.ModelForm):
    """
    A form for creating and updating Group instances.
    """

    class Meta:
        model = Group
        fields = [
            "name",
            "image",
            "description",
            "location_city",
            "location_country",
        ]

    name = forms.CharField(
        max_length=50,
        required=True,
        label="Group Name",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "id": "group_name",
                "name": "group_name",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 ",
                    "text-gray-900 text-sm rounded-lg ",
                    "focus:ring-primary-600 focus:border-primary-600 ",
                    "block w-full p-2.5",
                ),
            }
        ),
    )

    description = forms.CharField(
        required=True,
        label="Description",
        widget=forms.Textarea(
            attrs={
                "rows": 8,
                "autocomplete": "off",
                "id": "group_description",
                "name": "group_description",
                "class": (
                    "bg-gray-50 border border-gray-300 ",
                    "text-gray-900 text-sm rounded-lg ",
                    "focus:ring-primary-600 focus:border-primary-600 ",
                    "block w-full p-2.5",
                ),
            }
        ),
    )

    location_country = CountryField().formfield(
        required=True,
        label="Country",
        widget=forms.Select(
            attrs={
                "autocomplete": "off",
                "id": "location_country",
                "name": "location_country",
                "class": (
                    "bg-gray-50 border border-gray-300 ",
                    "text-gray-900 text-sm rounded-lg ",
                    "focus:ring-primary-600 focus:border-primary-600 ",
                    "block w-full p-2.5",
                ),
            }
        ),
    )

    location_city = forms.CharField(
        label="City",
        required=True,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "id": "location_city",
                "name": "location_city",
                "class": (
                    "bg-gray-50 border border-gray-300 ",
                    "text-gray-900 text-sm rounded-lg ",
                    "focus:ring-primary-600 focus:border-primary-600 ",
                    "block w-full p-2.5",
                ),
            }
        ),
    )

    image = CloudinaryFileField(
        required=False,
        options={
            "folder": "kns/images/groups/",
        },
    )
