from datetime import date, timedelta

from django.test import TestCase

from kns.core.models import Setting
from kns.custom_user.models import User
from kns.profiles import constants as profile_constants
from kns.profiles.forms import (
    BioDetailsForm,
    ContactDetailsForm,
    ProfileInvolvementForm,
    ProfileSettingsForm,
    ProfileSkillsForm,
)
from kns.skills.models import Skill


class TestProfileSettingsForm(TestCase):
    def setUp(self):
        """
        Create a user and associated profile for testing.
        """

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

    def test_profile_settings_form_initial(self):
        """
        Test the initial state of the ProfileSettingsForm.
        """
        form = ProfileSettingsForm(instance=self.profile)

        # Ensure that fields are not required by default
        self.assertFalse(
            form.fields["bio_details_is_visible"].required,
        )
        self.assertFalse(
            form.fields["contact_details_is_visible"].required,
        )

    def test_profile_settings_form_valid_data(self):
        """
        Test the ProfileSettingsForm with valid data.
        """
        form_data = {
            "bio_details_is_visible": True,
            "contact_details_is_visible": False,
        }
        form = ProfileSettingsForm(
            data=form_data,
            instance=self.profile,
        )
        self.assertTrue(form.is_valid())

        # Save the form and check the changes
        form.save()
        self.profile.refresh_from_db()

        self.assertTrue(self.profile.bio_details_is_visible)
        self.assertFalse(self.profile.contact_details_is_visible)


class TestBioDetailsForm(TestCase):
    def setUp(self):
        """
        Set up a user and profile for testing and mock the settings.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        # Mock the setting for min_registration_age
        self.setting = Setting.get_or_create_setting()
        self.setting.min_registration_age = 18
        self.setting.save()

    def test_bio_details_form_initial(self):
        """
        Test the initial state of the BioDetailsForm.
        """
        form = BioDetailsForm(instance=self.profile)

        # Ensure that all fields have the correct initial configuration
        self.assertTrue(form.fields["first_name"].required)
        self.assertTrue(form.fields["last_name"].required)
        self.assertTrue(form.fields["gender"].required)
        self.assertTrue(form.fields["date_of_birth"].required)
        self.assertFalse(form.fields["place_of_birth_country"].required)
        self.assertFalse(form.fields["place_of_birth_city"].required)

    def test_bio_details_form_valid_data(self):
        """
        Test the BioDetailsForm with valid data.
        """
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "gender": profile_constants.GENDER_OPTIONS[0][
                0
            ],  # Assuming choices are tuples
            "date_of_birth": date(2000, 1, 1),
            "place_of_birth_country": "US",
            "place_of_birth_city": "New York",
        }
        form = BioDetailsForm(data=form_data, instance=self.profile)

        self.assertTrue(form.is_valid())

        # Save the form and check the changes
        form.save()
        self.profile.refresh_from_db()

        self.assertEqual(self.profile.first_name, "John")
        self.assertEqual(self.profile.last_name, "Doe")
        self.assertEqual(self.profile.gender, profile_constants.GENDER_OPTIONS[0][0])
        self.assertEqual(self.profile.date_of_birth, date(2000, 1, 1))
        self.assertEqual(self.profile.place_of_birth_country, "US")
        self.assertEqual(self.profile.place_of_birth_city, "New York")

    def test_bio_details_form_invalid_age(self):
        """
        Test the BioDetailsForm with a date_of_birth that makes the user underage.
        """
        min_registration_age = self.setting.min_registration_age
        underage_dob = date.today() - timedelta(days=(min_registration_age * 365) - 1)

        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "gender": profile_constants.GENDER_OPTIONS[0][0],
            "date_of_birth": underage_dob,
        }
        form = BioDetailsForm(data=form_data, instance=self.profile)

        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)
        self.assertEqual(
            form.errors["date_of_birth"][0],
            f"Must be at least {min_registration_age} years old to register.",
        )

    def test_bio_details_form_missing_required_fields(self):
        """
        Test the BioDetailsForm with missing required fields.
        """
        form_data = {
            "first_name": "",
            "last_name": "",
            "gender": "",
            "date_of_birth": "",
        }
        form = BioDetailsForm(data=form_data, instance=self.profile)

        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("gender", form.errors)
        self.assertIn("date_of_birth", form.errors)

    def test_bio_details_form_edge_case_age(self):
        """
        Test the BioDetailsForm with a date_of_birth exactly on the boundary of the minimum age.
        """
        min_registration_age = self.setting.min_registration_age
        edge_case_dob = date.today() - timedelta(days=(min_registration_age * 365))

        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "gender": profile_constants.GENDER_OPTIONS[0][0],
            "date_of_birth": edge_case_dob,
        }
        form = BioDetailsForm(data=form_data, instance=self.profile)

        self.assertTrue(form.is_valid())


class TestProfileInvolvementForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

    def test_valid_form_when_all_facilitator_options_are_true(self):
        """Test that the form is valid when all facilitator options are set to True."""
        form_data = {
            "is_movement_training_facilitator": True,
            "is_skill_training_facilitator": True,
            "is_mentor": True,
        }

        form = ProfileInvolvementForm(
            data=form_data,
            instance=self.profile,
        )

        self.assertTrue(
            form.is_valid(), "The form should be valid when all facilitators are True"
        )

    def test_valid_form_with_reason_for_all_facilitator_options_false(self):
        """
        Test that the form is valid when all facilitator options are
        False and reasons are provided.
        """

        form_data = {
            "is_movement_training_facilitator": False,
            "reason_is_not_movement_training_facilitator": "Not interested.",
            "is_skill_training_facilitator": False,
            "reason_is_not_skill_training_facilitator": "Not enough time.",
            "is_mentor": False,
            "reason_is_not_mentor": "Lack of experience.",
        }

        form = ProfileInvolvementForm(data=form_data, instance=self.profile)

        self.assertTrue(
            form.is_valid(),
            "The form should be valid when reasons are provided for all False options",
        )

    def test_invalid_form_when_facilitator_options_false_without_reason(self):
        """
        Test that the form is invalid when any facilitator option is
        False without a corresponding reason.
        """
        form_data = {
            "is_movement_training_facilitator": False,
            "is_skill_training_facilitator": False,
            "reason_is_not_skill_training_facilitator": "Not enough time.",
            "is_mentor": False,
            "reason_is_not_mentor": "Lack of experience.",
        }

        form = ProfileInvolvementForm(
            data=form_data,
            instance=self.profile,
        )

        self.assertFalse(
            form.is_valid(),
            "The form should be invalid when a reason is missing for any False option",
        )

        self.assertIn(
            "reason_is_not_movement_training_facilitator",
            form.errors,
        )

    def test_invalid_form_when_no_facilitator_option_selected(self):
        """Test that the form is invalid when no facilitator options are selected."""
        form_data = {
            "is_movement_training_facilitator": None,
            "is_skill_training_facilitator": None,
            "is_mentor": None,
        }

        form = ProfileInvolvementForm(data=form_data, instance=self.profile)

        self.assertFalse(
            form.is_valid(),
            "The form should be invalid when no facilitator options are selected",
        )

    def test_invalid_form_when_only_some_reasons_are_provided(self):
        """Test that the form is invalid when only some reasons are provided."""
        form_data = {
            "is_movement_training_facilitator": False,
            "is_skill_training_facilitator": False,
            "reason_is_not_skill_training_facilitator": "Not enough time.",
            "is_mentor": False,
        }

        form = ProfileInvolvementForm(
            data=form_data,
            instance=self.profile,
        )

        self.assertFalse(
            form.is_valid(),
            "The form should be invalid when only some reasons are provided",
        )

        self.assertIn(
            "reason_is_not_movement_training_facilitator",
            form.errors,
        )

        self.assertIn(
            "reason_is_not_mentor",
            form.errors,
        )

    def test_valid_form_with_mixed_facilitator_options(self):
        """Test that the form is valid with mixed facilitator options and corresponding reasons."""
        form_data = {
            "is_movement_training_facilitator": True,
            "is_skill_training_facilitator": False,
            "reason_is_not_skill_training_facilitator": "Not enough time.",
            "is_mentor": True,
        }

        form = ProfileInvolvementForm(
            data=form_data,
            instance=self.profile,
        )

        self.assertTrue(
            form.is_valid(),
            "The form should be valid with mixed facilitator options and reasons",
        )


class TestContactDetailsForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

    def test_valid_form_with_all_fields_filled(self):
        """Test that the form is valid when all fields are correctly filled."""
        form_data = {
            "phone": "123456789",
            "email": "testuser@example.com",
            "phone_prefix": "+1",
            "location_city": "New York",
            "location_country": "US",
        }

        form = ContactDetailsForm(
            data=form_data,
            instance=self.profile,
        )

        self.assertTrue(
            form.is_valid(),
            "The form should be valid when all fields are correctly filled",
        )

    def test_invalid_form_without_email(self):
        """Test that the form is invalid if the email is missing when required."""
        form_data = {
            "phone": "123456789",
            "phone_prefix": "+1",
            "location_city": "New York",
            "location_country": "US",
        }

        form = ContactDetailsForm(
            data=form_data,
            instance=self.profile,
        )

        self.assertFalse(
            form.is_valid(),
            "The form should be invalid when the email is missing",
        )

        self.assertIn("email", form.errors)

    def test_clean_email_with_no_value_and_field_not_required(self):
        """
        Test that clean_email returns None when the email is not
        required and no value is provided.
        """
        form_data = {
            "phone": "123456789",
            "phone_prefix": "+1",
            "location_city": "New York",
            "location_country": "US",
            "email": "",
        }

        form = ContactDetailsForm(
            data=form_data,
            instance=self.profile,
        )
        form.fields["email"].required = False

        self.assertTrue(
            form.is_valid(),
            (
                "The form should be valid when the email field is not "
                "required and no value is provided"
            ),
        )
        self.assertIsNone(
            form.clean_email(),
            (
                "The clean_email method should return None if email is not "
                "required and no value is provided"
            ),
        )

    def test_valid_form_with_disabled_email(self):
        """Test that the form is valid when the email field is disabled."""
        form_data = {
            "phone": "123456789",
            "phone_prefix": "+1",
            "location_city": "New York",
            "location_country": "US",
        }

        form = ContactDetailsForm(
            data=form_data,
            instance=self.profile,
            show_email=False,
        )

        self.assertTrue(
            form.is_valid(),
            "The form should be valid when the email field is disabled",
        )

    def test_clean_email_with_valid_value(self):
        """Test that clean_email returns the email when a valid email is provided."""
        form_data = {
            "email": "validemail@example.com",
            "phone": "1234567890",  # Include optional fields to ensure validity
            "phone_prefix": "+1",
        }

        form = ContactDetailsForm(
            data=form_data,
            instance=self.profile,
        )

        print(form.errors)  # Debugging line

        self.assertTrue(
            form.is_valid(),
            "The form should be valid when a valid email is provided",
        )
        self.assertEqual(
            form.clean_email(),
            "validemail@example.com",
            "The clean_email method should return the valid email",
        )


class TestProfileSkillsForm(TestCase):
    def setUp(self):
        """
        Create a user, mock settings, and create some skills.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.settings = Setting.get_or_create_setting()

        self.settings.max_skills_per_user = 3
        self.settings.max_interests_per_user = 2

        self.settings.save()

        self.skill1 = Skill.objects.create(
            title="Skill 1",
            content="This is test content for a skill",
            author=self.profile,
        )
        self.skill2 = Skill.objects.create(
            title="Skill 2",
            content="This is test content for a skill",
            author=self.profile,
        )
        self.skill3 = Skill.objects.create(
            title="Skill 3",
            content="This is test content for a skill",
            author=self.profile,
        )
        self.skill4 = Skill.objects.create(
            title="Skill 4",
            content="This is test content for a skill",
            author=self.profile,
        )

    def test_valid_form(self):
        """
        Test that the form is valid when selecting a valid number of skills and interests.
        """
        form_data = {
            "skills": [self.skill1.id, self.skill2.id],
            "interests": [self.skill3.id],
        }

        form = ProfileSkillsForm(data=form_data)

        self.assertTrue(
            form.is_valid(),
            "Form should be valid with valid data",
        )

    def test_invalid_form_with_too_many_skills(self):
        """
        Test that the form is invalid when selecting more skills than allowed.
        """
        form_data = {
            "skills": [self.skill1.id, self.skill2.id, self.skill3.id, self.skill4.id],
            "interests": [self.skill1.id],
        }

        form = ProfileSkillsForm(data=form_data)

        self.assertFalse(
            form.is_valid(),
            "Form should be invalid with too many skills",
        )

        self.assertIn(
            "skills",
            form.errors,
        )

        self.assertEqual(
            form.errors["skills"][0],
            f"You can select up to {self.settings.max_skills_per_user} skills.",
        )

    def test_invalid_form_with_too_many_interests(self):
        """
        Test that the form is invalid when selecting more interests than allowed.
        """
        form_data = {
            "skills": [self.skill1.id],
            "interests": [
                self.skill2.id,
                self.skill3.id,
                self.skill4.id,
            ],
        }
        form = ProfileSkillsForm(data=form_data)

        self.assertFalse(
            form.is_valid(),
            "Form should be invalid with too many interests",
        )
        self.assertIn(
            "interests",
            form.errors,
        )

        self.assertEqual(
            form.errors["interests"][0],
            f"You can select up to {self.settings.max_interests_per_user} interests.",
        )

    def test_valid_form_with_empty_skills_and_interests(self):
        """
        Test that the form is valid when no skills or interests are selected.
        """
        form_data = {
            "skills": [],
            "interests": [],
        }

        form = ProfileSkillsForm(data=form_data)

        self.assertTrue(
            form.is_valid(),
            "Form should be valid with no skills or interests selected",
        )
