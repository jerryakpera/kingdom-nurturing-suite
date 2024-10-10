"""
Forms for `groups`.
"""

from cloudinary.forms import CloudinaryFileField
from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django_countries.fields import CountryField

from kns.faith_milestones.models import FaithMilestone
from kns.mentorships.models import MentorshipArea
from kns.profiles.models import Profile
from kns.skills.models import Skill
from kns.vocations.models import Vocation

from . import constants
from .models import Group


class GroupForm(forms.ModelForm):
    """
    A form for creating and updating Group instances.
    """

    class Meta:
        """
        Meta class for the GroupForm form.
        """

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
                "data-minlength": constants.GROUP_DESCRIPTION_MIN_LENGTH,
                "data-maxlength": constants.GROUP_DESCRIPTION_MAX_LENGTH,
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

    location_country = CountryField().formfield(
        required=False,
        label="Country",
        help_text="Filter groups by the country they are in",
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


class GroupMembersFilterForm(forms.Form):
    """
    A form for filtering Group instances based on the number of various roles.

    This form allows users to filter groups by the number of members,
    leaders, skill trainers, movement trainers, mentors, and external persons.
    All fields are optional, and the form is designed to support flexible filtering.

    Attributes
    ----------
    num_members : IntegerField
        An integer field for filtering groups by the number of members.
    num_leaders : IntegerField
        An integer field for filtering groups by the number of leaders.
    num_skill_trainers : IntegerField
        An integer field for filtering groups by the number of skill trainers.
    num_movement_trainers : IntegerField
        An integer field for filtering groups by the number of movement trainers.
    num_mentors : IntegerField
        An integer field for filtering groups by the number of mentors.
    num_external_persons : IntegerField
        An integer field for filtering groups by the number of external persons.
    """

    num_members = forms.IntegerField(
        required=False,
        label="Number of Members",
        help_text="Filter groups by the number of members",
        widget=forms.NumberInput(
            attrs={
                "id": "num_members_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    num_leaders = forms.IntegerField(
        required=False,
        label="Number of Leaders",
        help_text="Filter groups by the number of leaders",
        widget=forms.NumberInput(
            attrs={
                "id": "num_leaders_filter",
                "name": "num_leaders_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    num_skill_trainers = forms.IntegerField(
        required=False,
        label="Number of Skill Trainers",
        help_text="Filter groups by the number of skill trainers",
        widget=forms.NumberInput(
            attrs={
                "id": "num_skill_trainers_filter",
                "name": "num_skill_trainers_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    num_movement_trainers = forms.IntegerField(
        required=False,
        label="Number of Movement Trainers",
        help_text="Filter groups by the number of movement trainers",
        widget=forms.NumberInput(
            attrs={
                "id": "num_movement_trainers_filter",
                "name": "num_movement_trainers_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    num_mentors = forms.IntegerField(
        required=False,
        label="Number of Mentors",
        help_text="Filter groups by the number of mentors",
        widget=forms.NumberInput(
            attrs={
                "id": "num_mentors_filter",
                "name": "num_mentors_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    num_external_persons = forms.IntegerField(
        required=False,
        label="Number of External Persons",
        help_text="Filter groups by the number of external persons",
        widget=forms.NumberInput(
            attrs={
                "id": "num_external_persons_filter",
                "name": "num_external_persons_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    def clean_num_members(self):
        """
        Validate that the number of members is non-negative.

        Returns
        -------
        int or None
            The cleaned number of members if valid, or None.

        Raises
        ------
        ValidationError
            If the number of members is negative.
        """
        return self.clean_non_negative("num_members")

    def clean_num_leaders(self):
        """
        Validate that the number of leaders is non-negative.

        Returns
        -------
        int or None
            The cleaned number of leaders if valid, or None.

        Raises
        ------
        ValidationError
            If the number of leaders is negative.
        """
        return self.clean_non_negative("num_leaders")

    def clean_num_skill_trainers(self):
        """
        Validate that the number of skill trainers is non-negative.

        Returns
        -------
        int or None
            The cleaned number of skill trainers if valid, or None.

        Raises
        ------
        ValidationError
            If the number of skill trainers is negative.
        """
        return self.clean_non_negative("num_skill_trainers")

    def clean_num_movement_trainers(self):
        """
        Validate that the number of movement trainers is non-negative.

        Returns
        -------
        int or None
            The cleaned number of movement trainers if valid, or None.

        Raises
        ------
        ValidationError
            If the number of movement trainers is negative.
        """
        return self.clean_non_negative("num_movement_trainers")

    def clean_num_mentors(self):
        """
        Validate that the number of mentors is non-negative.

        Returns
        -------
        int or None
            The cleaned number of mentors if valid, or None.

        Raises
        ------
        ValidationError
            If the number of mentors is negative.
        """
        return self.clean_non_negative("num_mentors")

    def clean_num_external_persons(self):
        """
        Validate that the number of external persons is non-negative.

        Returns
        -------
        int or None
            The cleaned number of external persons if valid, or None.

        Raises
        ------
        ValidationError
            If the number of external persons is negative.
        """
        return self.clean_non_negative("num_external_persons")

    def clean_non_negative(self, field_name):
        """
        Ensure that the value for the given field is non-negative.

        Parameters
        ----------
        field_name : str
            The name of the field being validated.

        Returns
        -------
        int or None
            The cleaned value if valid, or None.

        Raises
        ------
        ValidationError
            If the value is negative.
        """
        value = self.cleaned_data.get(field_name)
        if value is not None and value < 0:
            raise forms.ValidationError(
                f"{field_name.replace('_', ' ').title()} cannot be negative."
            )
        return value


class GroupDemographicsFilterForm(forms.Form):
    """
    A form for filtering Group instances based on demographic criteria.

    This form allows users to filter groups by the number of male and female members,
    as well as by the criteria of having more male or female members.
    All fields are optional, and the form is designed to support flexible filtering.

    Attributes
    ----------
    num_male_members : IntegerField
        An integer field for filtering groups by the number of male members.
    num_female_members : IntegerField
        An integer field for filtering groups by the number of female members.
    more_male_members : BooleanField
        A boolean field for filtering groups with more male than female members.
    more_female_members : BooleanField
        A boolean field for filtering groups with more female than male members.
    """

    num_male_members = forms.IntegerField(
        required=False,
        label="Number of Male Members",
        help_text="Filter groups by the number of male members",
        widget=forms.NumberInput(
            attrs={
                "id": "num_male_members_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    num_female_members = forms.IntegerField(
        required=False,
        label="Number of Female Members",
        help_text="Filter groups by the number of female members",
        widget=forms.NumberInput(
            attrs={
                "id": "num_female_members_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    more_male_members = forms.BooleanField(
        required=False,
        label="More Male Members",
        help_text="Filter groups that have more male members than female",
        widget=forms.CheckboxInput(
            attrs={
                "id": "more_male_members_filter",
                "class": "form-check-input",
            }
        ),
    )

    more_female_members = forms.BooleanField(
        required=False,
        label="More Female Members",
        help_text="Filter groups that have more female members than male",
        widget=forms.CheckboxInput(
            attrs={
                "id": "more_female_members_filter",
                "class": "form-check-input",
            }
        ),
    )

    def clean_num_male_members(self):
        """
        Validate that the number of male members is non-negative.

        Returns
        -------
        int or None
            The cleaned number of male members if valid, or None.

        Raises
        ------
        ValidationError
            If the number of male members is negative.
        """
        return self.clean_non_negative("num_male_members")

    def clean_num_female_members(self):
        """
        Validate that the number of female members is non-negative.

        Returns
        -------
        int or None
            The cleaned number of female members if valid, or None.

        Raises
        ------
        ValidationError
            If the number of female members is negative.
        """
        return self.clean_non_negative("num_female_members")

    def clean_non_negative(self, field_name):
        """
        Ensure that the value for the given field is non-negative.

        Parameters
        ----------
        field_name : str
            The name of the field being validated.

        Returns
        -------
        int or None
            The cleaned value if valid, or None.

        Raises
        ------
        ValidationError
            If the value is negative.
        """
        value = self.cleaned_data.get(field_name)
        if value is not None and value < 0:
            raise forms.ValidationError(
                f"{field_name.replace('_', ' ').title()} cannot be negative."
            )
        return value


class GroupSkillsInterestsFilterForm(forms.Form):
    """
    A form for filtering Group instances based on skills and interests criteria.

    This form allows users to filter groups by unique skills, interests,
    and the number of skill and movement training facilitators.
    All fields are optional, and the form is designed to support flexible filtering.

    Attributes
    ----------
    skills : ModelMultipleChoiceField
        A multiple choice field to filter groups by the skills that members possess.
    unique_skills_count : IntegerField
        An integer field for filtering groups by the number of unique skills.
    interests : ModelMultipleChoiceField
        A multiple choice field to filter groups by the interests that members possess.
    unique_interests_count : IntegerField
        An integer field for filtering groups by the number of unique interests.
    """

    skills = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Skill.objects.all(),
        help_text="Filter by the skills that members in the group possess",
        widget=forms.SelectMultiple(
            attrs={
                "id": "skills_filter",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            }
        ),
    )

    unique_skills_count = forms.IntegerField(
        required=False,
        label="Unique Skills Count",
        help_text="Filter groups by the number of unique skills",
        widget=forms.NumberInput(
            attrs={
                "id": "unique_skills_count_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    interests = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Skill.objects.all(),
        help_text="Filter by the interests that members in the group possess",
        widget=forms.SelectMultiple(
            attrs={
                "id": "interests_filter",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            }
        ),
    )

    unique_interests_count = forms.IntegerField(
        required=False,
        label="Unique Interests Count",
        help_text="Filter groups by the number of unique interests",
        widget=forms.NumberInput(
            attrs={
                "id": "unique_interests_count_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    def clean(self):
        """
        Perform validation on the form fields.

        This method checks that the `unique_skills_count` and `unique_interests_count`
        are positive numbers and do not exceed the maximum allowed value. It adds errors
        to the form if these conditions are violated.

        Returns
        -------
        dict
            The cleaned form data.

        Raises
        ------
        ValidationError
            If any of the form fields contain invalid data.
        """
        cleaned_data = super().clean()
        unique_skills_count = cleaned_data.get("unique_skills_count")
        unique_interests_count = cleaned_data.get("unique_interests_count")

        # Define a maximum reasonable value
        MAX_REASONABLE_VALUE = 50

        if unique_skills_count is not None:
            if unique_skills_count < 0:
                self.add_error(
                    "unique_skills_count",
                    "Must be a positive number.",
                )

            elif unique_skills_count > MAX_REASONABLE_VALUE:
                self.add_error(
                    "unique_skills_count",
                    f"Must not exceed {MAX_REASONABLE_VALUE}.",
                )

        if unique_interests_count is not None:
            if unique_interests_count < 0:
                self.add_error("unique_interests_count", "Must be a positive number.")

            elif unique_interests_count > MAX_REASONABLE_VALUE:
                self.add_error(
                    "unique_interests_count",
                    f"Must not exceed {MAX_REASONABLE_VALUE}.",
                )

        return cleaned_data


class GroupVocationsFilterForm(forms.Form):
    """
    A form for filtering Group instances based on vocations criteria.

    This form allows users to filter groups by the vocations that group members possess.
    All fields are optional, and the form supports flexible filtering by allowing
    multiple vocations to be selected or filtering by the number of unique vocations.

    Attributes
    ----------
    vocations : ModelMultipleChoiceField
        A multiple choice field to filter groups by the vocations that members possess.
    unique_vocations_count : IntegerField
        An integer field for filtering groups by the number of unique vocations.
    """

    vocations = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Vocation.objects.all(),
        help_text="Filter by the vocations that members in the group possess",
        widget=forms.SelectMultiple(
            attrs={
                "id": "vocations_filter",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            }
        ),
    )

    unique_vocations_count = forms.IntegerField(
        required=False,
        label="Unique Vocations Count",
        help_text="Filter groups by the number of unique vocations",
        widget=forms.NumberInput(
            attrs={
                "id": "unique_vocations_count_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    def clean(self):
        """
        Perform validation on the form fields.

        This method checks that `unique_vocations_count` is a positive number
        and does not exceed the maximum allowed value. Errors are added if these
        conditions are not met.

        Returns
        -------
        dict
            The cleaned form data.

        Raises
        ------
        ValidationError
            If the form fields contain invalid data.
        """
        cleaned_data = super().clean()
        unique_vocations_count = cleaned_data.get("unique_vocations_count")

        # Define a maximum reasonable value
        MAX_REASONABLE_VALUE = 50

        if unique_vocations_count is not None:
            if unique_vocations_count < 0:
                self.add_error(
                    "unique_vocations_count",
                    "Must be a positive number.",
                )

            elif unique_vocations_count > MAX_REASONABLE_VALUE:
                self.add_error(
                    "unique_vocations_count",
                    f"Must not exceed {MAX_REASONABLE_VALUE}.",
                )

        return cleaned_data


class GroupMentorshipAreasFilterForm(forms.Form):
    """
    A form for filtering Group instances based on mentorship areas criteria.

    This form allows users to filter groups by the mentorship areas that group members possess.
    All fields are optional, and the form supports flexible filtering by allowing
    multiple mentorship areas to be selected or filtering by the number of unique mentorship areas.

    Attributes
    ----------
    mentorship_areas : ModelMultipleChoiceField
        A multiple choice field to filter groups by the mentorship areas that members possess.
    unique_mentorship_areas_count : IntegerField
        An integer field for filtering groups by the number of unique mentorship areas.
    """

    mentorship_areas = forms.ModelMultipleChoiceField(
        required=False,
        queryset=MentorshipArea.objects.all(),
        help_text="Filter by the mentorship areas that members in the group possess",
        widget=forms.SelectMultiple(
            attrs={
                "id": "mentorship_areas_filter",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            }
        ),
    )

    unique_mentorship_areas_count = forms.IntegerField(
        required=False,
        label="Unique Mentorship Areas Count",
        help_text="Filter groups by the number of unique mentorship areas",
        widget=forms.NumberInput(
            attrs={
                "id": "unique_mentorship_areas_count_filter",
                "autocomplete": "off",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    def clean(self):
        """
        Perform validation on the form fields.

        This method checks that `unique_mentorship_areas_count` is a positive number
        and does not exceed the maximum allowed value. Errors are added if these
        conditions are not met.

        Returns
        -------
        dict
            The cleaned form data.

        Raises
        ------
        ValidationError
            If the form fields contain invalid data.
        """
        cleaned_data = super().clean()
        unique_mentorship_areas_count = cleaned_data.get(
            "unique_mentorship_areas_count"
        )

        # Define a maximum reasonable value
        MAX_REASONABLE_VALUE = 50

        if unique_mentorship_areas_count is not None:
            if unique_mentorship_areas_count < 0:
                self.add_error(
                    "unique_mentorship_areas_count",
                    "Must be a positive number.",
                )

            elif unique_mentorship_areas_count > MAX_REASONABLE_VALUE:
                self.add_error(
                    "unique_mentorship_areas_count",
                    f"Must not exceed {MAX_REASONABLE_VALUE}.",
                )

        return cleaned_data


class GroupFaithMilestoneFilterForm(forms.Form):
    """
    A form for filtering Group instances based on faith milestones.

    This form allows users to filter groups by the faith milestones that they have achieved.
    All fields are optional, and the form supports flexible filtering by allowing
    multiple faith milestones to be selected.

    Attributes
    ----------
    faith_milestones : ModelMultipleChoiceField
        A multiple choice field to filter groups by the faith milestones that they have achieved.
    """

    faith_milestones = forms.ModelMultipleChoiceField(
        label="Faith Milestones",
        queryset=FaithMilestone.objects.filter(type="group"),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 "
                    "text-sm rounded-lg focus:ring-blue-500 "
                    "focus:border-blue-500 block w-full p-2.5"
                ),
            }
        ),
        help_text=(
            "Filter groups by the faith milestones that groups should have achieved. "
            "Hold Ctrl to select multiple milestones."
        ),
    )


class MoveToSisterGroupForm(forms.Form):
    """
    A form for moving a member to a sister group.

    This form allows users to move a member from their current group
    to a sister group, with both groups sharing the same parent group.
    The member must belong to the current group, and the target group
    must be a sibling group.

    Parameters
    ----------
    *args : tuple
        Positional arguments passed to the parent form.
    **kwargs : dict
        Keyword arguments passed to the parent form. 'leader_group' must be
        included in kwargs to filter the 'member' and 'target_group' fields.
    """

    member = forms.ModelChoiceField(
        queryset=Profile.objects.none(),
        label="Select the member of your group to move",
        required=True,
        widget=forms.Select(
            attrs={
                "id": "member",
                "name": "member",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    target_group = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        label="Select the group to transfer the member to",
        required=True,
        widget=forms.Select(
            attrs={
                "id": "target_group",
                "name": "target_group",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with a queryset for the 'member' and 'target_group' fields.

        The 'member' field is populated with profiles from the current leader's group.
        The 'target_group' field is populated with sibling groups, excluding the
        current leader's group.

        Parameters
        ----------
        *args : tuple
            Positional arguments passed to the parent form.
        **kwargs : dict
            Keyword arguments passed to the parent form. 'leader_group' must be
            included in kwargs to filter the 'member' and 'target_group' fields.
        """
        leader_group = kwargs.pop("leader_group")
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = Profile.objects.filter(
            group_in__group=leader_group,
        )
        self.fields["target_group"].queryset = Group.objects.filter(
            parent=leader_group.parent
        ).exclude(id=leader_group.id)

    def clean_target_group(self):
        """
        Validate and clean the 'target_group' field.

        Ensures that the selected target group is valid for moving the member.

        Returns
        -------
        Group
            The cleaned target group instance.
        """
        target_group = self.cleaned_data["target_group"]
        return target_group


class MoveToChildGroupForm(forms.Form):
    """
    A form for moving a member to a child group.

    This form allows users to move a member from their current group to
    one of its child groups. The member must belong to the current group,
    and the target group must be a child group.

    Parameters
    ----------
    *args : tuple
        Positional arguments passed to the parent form.
    **kwargs : dict
        Keyword arguments passed to the parent form. 'leader_group' must be
        included in kwargs to filter the 'member' and 'target_group' fields.
    """

    member = forms.ModelChoiceField(
        queryset=Profile.objects.none(),
        label="Select Member",
        required=True,
        widget=forms.Select(
            attrs={
                "id": "member",
                "name": "member",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    target_group = forms.ModelChoiceField(
        queryset=Group.objects.none(),
        label="Select Child Group",
        required=True,
        widget=forms.Select(
            attrs={
                "id": "target_group",
                "name": "target_group",
                "class": (
                    "bg-gray-50 border border-gray-300 text-gray-900 text-sm "
                    "rounded-lg focus:ring-primary-600 focus:border-primary-600 "
                    "block w-full p-2.5"
                ),
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with a queryset for the 'member' and 'target_group' fields.

        The 'member' field is populated with profiles from the current leader's group.
        The 'target_group' field is populated with child groups under the current leader's group.

        Parameters
        ----------
        *args : tuple
            Positional arguments passed to the parent form.
        **kwargs : dict
            Keyword arguments passed to the parent form. 'leader_group' must be
            included in kwargs to filter the 'member' and 'target_group' fields.
        """
        leader_group = kwargs.pop("leader_group")
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = Profile.objects.filter(
            group_in__group=leader_group,
        )
        self.fields["target_group"].queryset = Group.objects.filter(
            parent=leader_group,
        )

    def clean_target_group(self):
        """
        Validate and clean the 'target_group' field.

        Ensures that the selected target group is valid for moving the member.

        Returns
        -------
        Group
            The cleaned target group instance.
        """
        target_group = self.cleaned_data["target_group"]
        return target_group
