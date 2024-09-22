"""
Forms for `groups`.
"""

from cloudinary.forms import CloudinaryFileField
from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django_countries.fields import CountryField

from . import constants
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
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    description = forms.CharField(
        required=True,
        label="Description",
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "autocomplete": "off",
                "id": "group_description",
                "name": "group_description",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
        validators=[
            MinLengthValidator(
                constants.GROUP_DESCRIPTION_MIN_LENGTH,
                message="Description must be at least 10 characters long.",
            ),
            MaxLengthValidator(
                constants.GROUP_DESCRIPTION_MAX_LENGTH,
                message="Description cannot exceed 500 characters.",
            ),
        ],
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
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
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
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
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


class GroupBasicFilterForm(forms.Form):
    """
    A form for filtering Group instances based on various criteria.

    This form allows users to filter groups by their description,
    location (country and city), and the leader's name. All fields
    are optional, and the form is designed to support flexible filtering.
    """

    description = forms.CharField(
        required=False,
        label="Group Description",
        help_text="Filter groups by their description",
        widget=forms.TextInput(
            attrs={
                "id": "group_description_filter",
                "name": "group_description_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    location_country = forms.CharField(
        required=False,
        label="Country",
        help_text="Filter groups by the country they are in",
        widget=forms.TextInput(
            attrs={
                "id": "location_country_filter",
                "name": "location_country_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    location_city = forms.CharField(
        required=False,
        label="City",
        help_text="Filter groups by the city they are in",
        widget=forms.TextInput(
            attrs={
                "id": "location_city_filter",
                "name": "location_city_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    leader = forms.CharField(
        required=False,
        label="Leader",
        help_text="Filter groups by the leader's name",
        widget=forms.TextInput(
            attrs={
                "id": "leader_filter",
                "name": "leader_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )
