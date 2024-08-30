"""
Forms for the `profiles` app.
"""

from datetime import date, timedelta

from cloudinary.forms import CloudinaryFileField
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from kns.core.models import Setting
from kns.skills.models import Skill

from . import constants as profile_constants
from . import utils as profile_utils
from .models import ConsentForm, EncryptionReason, Profile


class BioDetailsForm(forms.ModelForm):
    """
    A form for collecting basic bio details of a user profile.

    This form allows users to input their first name, last name, gender, date of birth,
    place of birth (country and city).

    Parameters
    ----------
    *args : tuple
        Positional arguments passed to the parent class.
    **kwargs : dict
        Keyword arguments passed to the parent class.
    """

    class Meta:
        model = Profile
        fields = (
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "place_of_birth_country",
            "place_of_birth_city",
        )

    first_name = forms.CharField(
        strip=False,
        required=True,
        label="First name",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "id": "first_name",
                "name": "first_name",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    last_name = forms.CharField(
        strip=False,
        required=True,
        label="Last name",
        widget=forms.TextInput(
            attrs={
                "id": "last_name",
                "name": "last_name",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    gender = forms.ChoiceField(
        required=True,
        label="Gender",
        widget=forms.Select(
            attrs={
                "id": "gender",
                "name": "gender",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    date_of_birth = forms.DateField(
        label="Date of birth",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "autocomplete": "off",
                "id": "date_of_birth",
                "name": "date_of_birth",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    place_of_birth_country = CountryField().formfield(
        required=False,
        widget=forms.Select(
            attrs={
                "autocomplete": "off",
                "id": "place_of_birth_country",
                "name": "place_of_birth_country",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    place_of_birth_city = forms.CharField(
        required=False,
        label="Place of birth (city)",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "id": "place_of_birth_city",
                "name": "place_of_birth_city",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    def clean_date_of_birth(self):
        """
        Validate the date of birth to ensure the user meets the minimum age requirement.

        Returns
        -------
        date
            The validated date of birth.

        Raises
        ------
        ValidationError
            If the date of birth does not meet the minimum age requirement.
        """
        date_of_birth = self.cleaned_data.get("date_of_birth")
        min_registration_age = Setting.get_or_create_setting().min_registration_age

        if date_of_birth:
            min_allowed_date = date.today() - timedelta(
                days=(min_registration_age * 365),
            )
            if date_of_birth > min_allowed_date:
                raise forms.ValidationError(
                    f"Must be at least {min_registration_age} years old to register."
                )
        return date_of_birth

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with gender choices and date of birth restrictions.

        Parameters
        ----------
        *args : tuple
            Positional arguments passed to the parent class.
        **kwargs : dict
            Keyword arguments passed to the parent class.
        """
        super(BioDetailsForm, self).__init__(*args, **kwargs)
        self.fields["gender"].choices = profile_constants.GENDER_OPTIONS

        min_registration_age = Setting.get_or_create_setting().min_registration_age

        max_date_of_birth = profile_utils.calculate_max_dob(min_registration_age)

        self.fields["date_of_birth"].widget.attrs["max"] = max_date_of_birth


class ProfileInvolvementForm(forms.ModelForm):
    """
    A form for specifying the user's involvement in various training and mentoring roles.

    This form allows users to indicate their willingness to be a movement training facilitator,
    skill training facilitator, or mentor, and to provide reasons if they are not willing or able
    to fulfill these roles.

    Parameters
    ----------
    *args : tuple
        Positional arguments passed to the parent class.
    **kwargs : dict
        Keyword arguments passed to the parent class.
    """

    class Meta:
        model = Profile
        fields = [
            "is_movement_training_facilitator",
            "reason_is_not_movement_training_facilitator",
            "is_skill_training_facilitator",
            "reason_is_not_skill_training_facilitator",
            "is_mentor",
            "reason_is_not_mentor",
        ]

        help_texts = {
            "is_mentor": "Willing to facilitate mentor others?",
            "is_skill_training_facilitator": "Willing to facilitate skill trainings?",
            "is_movement_training_facilitator": "Willing to facilitate movement trainings?",
        }

    reason_is_not_movement_training_facilitator = forms.CharField(
        required=False,
        label="If not willing/able, what is the reason",
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
                "id": "reason_is_not_movement_training_facilitator",
                "name": "reason_is_not_movement_training_facilitator",
            }
        ),
    )

    reason_is_not_skill_training_facilitator = forms.CharField(
        required=False,
        label="If not willing/able, what is the reason",
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
                "id": "reason_is_not_skill_training_facilitator",
                "name": "reason_is_not_skill_training_facilitator",
            }
        ),
    )

    reason_is_not_mentor = forms.CharField(
        required=False,
        label="If not willing/able, what is the reason",
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "autocomplete": "off",
                "id": "reason_is_not_mentor",
                "name": "reason_is_not_mentor",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    def clean(self):
        """
        Validate the form to ensure that reasons are provided if the user is not willing
        or able to fulfill certain roles.

        Returns
        -------
        dict
            The cleaned data from the form.

        Raises
        ------
        ValidationError
            If required reasons are not provided.
        """
        cleaned_data = super().clean()
        is_movement_training_facilitator = cleaned_data.get(
            "is_movement_training_facilitator"
        )
        reason_is_not_movement_training_facilitator = cleaned_data.get(
            "reason_is_not_movement_training_facilitator"
        )

        is_skill_training_facilitator = cleaned_data.get(
            "is_skill_training_facilitator"
        )
        reason_is_not_skill_training_facilitator = cleaned_data.get(
            "reason_is_not_skill_training_facilitator"
        )

        is_mentor = cleaned_data.get("is_mentor")
        reason_is_not_mentor = cleaned_data.get("reason_is_not_mentor")

        if (
            not is_movement_training_facilitator
            and not reason_is_not_movement_training_facilitator
        ):
            self.add_error(
                "reason_is_not_movement_training_facilitator", "This field is required."
            )

        if (
            not is_skill_training_facilitator
            and not reason_is_not_skill_training_facilitator
        ):
            self.add_error(
                "reason_is_not_skill_training_facilitator", "This field is required."
            )

        if not is_mentor and not reason_is_not_mentor:
            self.add_error("reason_is_not_mentor", "This field is required.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_movement_training_facilitator"].widget.attrs[
            "id"
        ] = "is_movement_training_facilitator"
        self.fields["is_skill_training_facilitator"].widget.attrs[
            "id"
        ] = "is_skill_training_facilitator"
        self.fields["is_mentor"].widget.attrs["id"] = "is_mentor"


class ContactDetailsForm(forms.ModelForm):
    """
    A form for entering contact information for a user profile.

    Parameters
    ----------
    *args : tuple
        Positional arguments passed to the parent class.
    **kwargs : dict
        Keyword arguments passed to the parent class.
    """

    location_country = CountryField().formfield(
        required=False,
        widget=CountrySelectWidget(
            attrs={
                "autocomplete": "off",
                "id": "location_country",
                "name": "location_country",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    location_city = forms.CharField(
        required=False,
        label="Location (city)",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "id": "location_city",
                "name": "location_city",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    phone_prefix = forms.CharField(
        required=False,
        label=_("Phone code"),
        widget=forms.TextInput(
            attrs={
                "readonly": True,
                "id": "phone_prefix",
                "autocomplete": "off",
                "name": "phone_prefix",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    phone = forms.CharField(
        required=False,
        label=_("Phone"),
        widget=forms.TextInput(
            attrs={
                "id": "phone",
                "name": "phone",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "off",
                "id": "email",
                "name": "email",
                "class": (
                    "bg-gray-50 border border-gray-300"
                    "text-gray-900 text-sm rounded-lg focus:ring-blue-500"
                    "focus:border-blue-500 block w-full p-2.5 "
                ),
            }
        ),
    )

    class Meta:
        model = Profile
        fields = [
            "phone",
            "email",
            "phone_prefix",
            "location_city",
            "location_country",
        ]

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with the option to show or hide the email field.

        Parameters
        ----------
        *args
            Variable length argument list.
        **kwargs
            Arbitrary keyword arguments. Can include:
            - show_email (bool): If True (default), the email field is shown.
            If False, the email field is hidden and marked as not required.
        """
        show_email = kwargs.pop("show_email", True)

        super(ContactDetailsForm, self).__init__(*args, **kwargs)

        if not show_email:
            # Disable the field and mark it as not required
            self.fields["email"].widget.attrs["disabled"] = True
            self.fields["email"].required = False

    def clean_email(self):
        """
        Validate the email field.

        Returns
        -------
        str or None
            The cleaned email if valid or None if the email is not required and empty.
        """
        email = self.cleaned_data.get("email")

        if not email and not self.fields["email"].required:
            return None

        return email

    def clean_phone_prefix(self):
        """
        Validate the phone_prefix field.

        Returns
        -------
        str
            The cleaned phone_prefix if valid.

        Raises
        ------
        forms.ValidationError
            If phone_prefix is missing.
        """
        phone_prefix = self.cleaned_data.get("phone_prefix")

        if not phone_prefix:
            raise forms.ValidationError("This field is required.")

        return phone_prefix


class ProfileRoleForm(forms.ModelForm):
    """
    A form for selecting a role for a profile.

    This form uses a ChoiceField to allow users to select a role from
    predefined options.
    It is associated with the `Profile` model and only includes the `role` field.

    Attributes:
        role (forms.ChoiceField): A dropdown field for selecting a role.
        The choices are defined in `profile_constants.PROFILE_ROLE_OPTIONS`.
    """

    role = forms.ChoiceField(
        label="Role",
        required=True,
        choices=profile_constants.PROFILE_ROLE_OPTIONS,
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

    class Meta:
        """
        Meta options for the ProfileRoleForm.

        Specifies the model to be used with this form and the fields to include.
        """

        model = Profile
        fields = ["role"]


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

    def __init__(self, *args, **kwargs):  # pragma: no cover
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


class ProfilePictureForm(forms.ModelForm):  # pragma: no cover
    """
    A form for updating a profiles picture.
    """

    class Meta:
        model = Profile
        fields = [
            "image",
        ]

    image = CloudinaryFileField(
        required=False,
        options={"folder": "kns/images/profiles/"},
    )


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


class ProfileEncryptionForm(forms.Form):
    """
    Form for encrypting a profile. Allows the user to select a reason
    for hiding the profile's name from public view.

    Parameters
    ----------
    *args
        Variable length argument list.
    **kwargs
        Keyword arguments.

    Attributes
    ----------
    encryption_reason
        A ChoiceField that presents a dropdown of available encryption
        reasons fetched from the EncryptionReason model.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the ProfileEncryptionForm with dynamic choices for the
        encryption_reason field based on the EncryptionReason model.

        Parameters
        ----------
        *args
            Variable length argument list.
        **kwargs
            Keyword arguments.
        """
        super(ProfileEncryptionForm, self).__init__(*args, **kwargs)

        choices = (
            EncryptionReason.objects.all()
            .order_by("id")
            .values_list(
                "id",
                "title",
            )
        )

        self.fields["encryption_reason"] = forms.ChoiceField(
            required=False,
            choices=choices,
            label="Select the reason for hiding this user's name",
            widget=forms.Select(
                attrs={
                    "class": (
                        "bg-gray-50 border border-gray-300 text-gray-900 "
                        "text-sm rounded-lg focus:ring-blue-500 "
                        "focus:border-blue-500 block w-full p-2.5"
                    ),
                    "id": "encryption_reason",
                    "name": "encryption_reason",
                }
            ),
        )
