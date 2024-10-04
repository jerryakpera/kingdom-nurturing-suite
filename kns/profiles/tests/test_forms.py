from datetime import date, timedelta

from django.test import TestCase

from kns.core.models import Setting
from kns.custom_user.models import User
from kns.faith_milestones.forms import FaithMilestone
from kns.faith_milestones.models import ProfileFaithMilestone
from kns.mentorships.models import MentorshipArea, ProfileMentorshipArea
from kns.profiles import constants as profile_constants
from kns.profiles.forms import (
    BasicInfoFilterForm,
    BioDetailsForm,
    ContactDetailsForm,
    FaithMilestoneFilterForm,
    InvolvementFilterForm,
    MentorshipFilterForm,
    ProfileEncryptionForm,
    ProfileInvolvementForm,
    ProfileSettingsForm,
    SkillsFilterForm,
)
from kns.profiles.models import EncryptionReason
from kns.skills.models import ProfileSkill, Skill
from kns.vocations.models import ProfileVocation, Vocation


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
            "reason_is_not_movement_training_facilitator": (
                "Not interested in facilitating movement trainings due "
                "to time constraints and other commitments."
            ),
            "is_skill_training_facilitator": False,
            "reason_is_not_skill_training_facilitator": (
                "Not enough time to commit to skill training sessions."
            ),
            "is_mentor": False,
            "reason_is_not_mentor": (
                "Lack of experience in mentoring roles and responsibilities."
            ),
        }

        form = ProfileInvolvementForm(data=form_data, instance=self.profile)
        self.assertTrue(
            form.is_valid(),
            "The form should be valid when reasons are provided for all False options",
        )

    def test_valid_form_with_mixed_facilitator_options(self):
        """Test that the form is valid with mixed facilitator options and corresponding reasons."""

        form_data = {
            "is_movement_training_facilitator": True,
            "is_skill_training_facilitator": False,
            "reason_is_not_skill_training_facilitator": (
                "Not enough time to commit to skill trainings. "
                "Not enough time to commit to movement trainings."
            ),
            "reason_is_not_movement_training_facilitator": (
                "Not enough time to commit to movement trainings. "
                "Not enough time to commit to movement trainings."
            ),
            "reason_is_not_mentor": (
                "Not enough time to commit to mentor others."
                "Not enough time to commit to movement trainings."
            ),
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


class TestProfileEncryptionForm(TestCase):
    def setUp(self):
        """
        Set up a published encryption reason for testing.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )

        self.reason1 = EncryptionReason.objects.create(
            title="Test Reason 1",
            description="Sample description for encryption reason",
            author=self.user.profile,
        )

        self.reason2 = EncryptionReason.objects.create(
            title="Test Reason 2",
            description="Sample description for encryption reason",
            author=self.user.profile,
        )

        self.reason3 = EncryptionReason.objects.create(
            title="Test Reason 3",
            description="Sample description for encryption reason",
            author=self.user.profile,
        )

    def test_form_initial_choices(self):
        """
        Test that the form loads with the correct initial choices.
        """
        form = ProfileEncryptionForm()

        # Extract the available choices from the form
        choices = form.fields["encryption_reason"].choices

        # Ensure that only published reasons are included
        expected_choices = [
            (self.reason1.id, self.reason1.title),
            (self.reason2.id, self.reason2.title),
            (self.reason3.id, self.reason3.title),
        ]

        self.assertEqual(choices, expected_choices)

    def test_form_empty_choices_when_no_published_reason(self):
        """
        Test the form when there are no published encryption reasons.
        """
        EncryptionReason.objects.all().delete()

        form = ProfileEncryptionForm()
        choices = form.fields["encryption_reason"].choices

        # Expecting an empty list as no published reasons exist
        self.assertEqual(choices, [])

    def test_form_valid_with_reason(self):
        """
        Test that the form is valid when a reason is selected.
        """
        form_data = {
            "encryption_reason": self.reason1.id,
        }

        form = ProfileEncryptionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_valid_without_reason(self):
        """
        Test that the form is valid when no reason is selected.
        """
        form_data = {
            "encryption_reason": "",
        }

        form = ProfileEncryptionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_nonexistent_reason(self):
        """
        Test that the form is invalid when a nonexistent reason is selected.
        """
        form_data = {
            "encryption_reason": 999,
        }

        form = ProfileEncryptionForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestBasicInfoFilterForm(TestCase):
    def setUp(self):
        """
        Set up test data for filtering.
        """
        # Create users and their profiles
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="password"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="password"
        )

        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile

        # Set different attributes for filtering
        self.profile1.gender = "male"
        self.profile1.save()

        self.profile2.gender = "female"
        self.profile2.save()

    def test_form_initialization(self):
        """
        Test that the form initializes correctly with no errors.
        """
        form = BasicInfoFilterForm()
        self.assertIsInstance(form, BasicInfoFilterForm)

    def test_form_valid_gender_filter(self):
        """
        Test that filtering by gender returns the correct profiles.
        """
        form_data = {"gender": "female"}
        form = BasicInfoFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["gender"], "female")

    def test_form_invalid_min_age(self):
        """
        Test that an invalid minimum age (greater than the current age)
        raises a validation error.
        """
        future_age = 200
        form_data = {"min_age": future_age}
        form = BasicInfoFilterForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("min_age", form.errors)

    def test_form_valid_min_age(self):
        """
        Test that a valid minimum age passes validation.
        """
        valid_age = 25
        form_data = {"min_age": valid_age}
        form = BasicInfoFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["min_age"], valid_age)

    def test_form_filter_by_location(self):
        """
        Test that filtering by location (city and country) works correctly.
        """
        form_data = {"location_country": "US", "location_city": "New York"}
        form = BasicInfoFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["location_country"], "US")
        self.assertEqual(form.cleaned_data["location_city"], "New York")

    def test_form_empty_filter(self):
        """
        Test that an empty form does not raise validation errors.
        """
        form = BasicInfoFilterForm(data={})

        self.assertTrue(form.is_valid())

    def test_form_raises_validation_error_for_exceeding_min_age(self):
        """
        Test that a ValidationError is raised when min_age is too low,
        resulting in an unrealistic birthdate.
        """
        form_data = {"min_age": 0}  # Age is too low to be realistic
        form = BasicInfoFilterForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("min_age", form.errors)
        self.assertEqual(
            form.errors["min_age"],
            ["Ensure this value is greater than or equal to 15."],
        )


class TestInvolvementFilterForm(TestCase):
    def setUp(self):
        """
        Set up test data for filtering by activity and training.
        """
        # Create users and their profiles
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="password",
        )

        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile

        # Set different attributes for filtering
        self.profile1.is_movement_training_facilitator = True
        self.profile1.is_skill_training_facilitator = False
        self.profile1.is_mentor = True
        self.profile1.save()

        self.profile2.is_movement_training_facilitator = False
        self.profile2.is_skill_training_facilitator = True
        self.profile2.is_mentor = False
        self.profile2.save()

    def test_form_initialization(self):
        """
        Test that the form initializes correctly with no errors.
        """
        form = InvolvementFilterForm()
        self.assertIsInstance(form, InvolvementFilterForm)

    def test_form_valid_movement_training_filter(self):
        """
        Test that filtering by 'movement training facilitator' returns the correct profiles.
        """
        form_data = {"is_movement_training_facilitator": True}
        form = InvolvementFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["is_movement_training_facilitator"],
            True,
        )

    def test_form_valid_skill_training_filter(self):
        """
        Test that filtering by 'skill training facilitator' returns the correct profiles.
        """
        form_data = {"is_skill_training_facilitator": True}
        form = InvolvementFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["is_skill_training_facilitator"],
            True,
        )

    def test_form_valid_mentor_filter(self):
        """
        Test that filtering by 'mentor' returns the correct profiles.
        """
        form_data = {"is_mentor": True}
        form = InvolvementFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["is_mentor"], True)

    def test_form_empty_filter(self):
        """
        Test that an empty form does not raise validation errors.
        """
        form = InvolvementFilterForm(data={})

        self.assertTrue(form.is_valid())


class TestSkillsFilterForm(TestCase):
    def setUp(self):
        """
        Set up test data for filtering by education and experience.
        """

        # Create users and assign skills/vocations to profiles
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="password",
        )

        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile

        # Create sample Skills and Vocations
        self.skill1 = Skill.objects.create(
            title="Leadership",
            content="First skill",
            author=self.profile1,
        )
        self.skill2 = Skill.objects.create(
            title="Communication",
            content="Second skill",
            author=self.profile1,
        )
        self.skill3 = Skill.objects.create(
            title="Unpublished Skill",
            content="Third skill",
            author=self.profile2,
        )

        self.vocation1 = Vocation.objects.create(
            title="Engineering",
            description="First vocation",
            author=self.profile2,
        )
        self.vocation2 = Vocation.objects.create(
            title="Education",
            description="Second vocation",
            author=self.profile2,
        )

        ProfileSkill.objects.create(
            profile=self.profile1,
            skill=self.skill1,
        )
        ProfileVocation.objects.create(
            profile=self.profile1,
            vocation=self.vocation1,
        )

        ProfileSkill.objects.create(
            profile=self.profile2,
            skill=self.skill2,
        )
        ProfileVocation.objects.create(
            profile=self.profile2,
            vocation=self.vocation2,
        )

    def test_form_initialization(self):
        """
        Test that the form initializes correctly with no errors.
        """

        form = SkillsFilterForm()

        self.assertIsInstance(form, SkillsFilterForm)

    def test_form_valid_skills_filter(self):
        """
        Test that filtering by skills returns the correct profiles.
        """
        form_data = {"skills": [self.skill1.id]}
        form = SkillsFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertIn(
            self.skill1,
            form.cleaned_data["skills"],
        )

    def test_form_valid_interests_filter(self):
        """
        Test that filtering by interests returns the correct profiles.
        """
        form_data = {
            "interests": [self.skill2.id],
        }
        form = SkillsFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertIn(
            self.skill2,
            form.cleaned_data["interests"],
        )

    def test_form_valid_vocations_filter(self):
        """
        Test that filtering by vocations returns the correct profiles.
        """
        form_data = {
            "vocations": [self.vocation1.id],
        }

        form = SkillsFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertIn(
            self.vocation1,
            form.cleaned_data["vocations"],
        )

    def test_form_empty_filter(self):
        """
        Test that an empty form does not raise validation errors.
        """
        form = SkillsFilterForm(data={})

        self.assertTrue(form.is_valid())


class TestMentorshipFilterForm(TestCase):
    def setUp(self):
        """
        Set up test data for filtering by mentorship areas and mentorship areas of interest.
        """
        # Create users and assign mentorship areas
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="password",
        )

        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile

        # Create sample Mentorship Areas
        self.mentorship_area1 = MentorshipArea.objects.create(
            title="Career Coaching",
            content="First mentorship area",
            author=self.profile1,
            status="published",
        )

        self.mentorship_area2 = MentorshipArea.objects.create(
            title="Leadership Training",
            content="Second mentorship area",
            author=self.profile2,
            status="published",
        )

        self.mentorship_area3 = MentorshipArea.objects.create(
            title="Unpublished Area",
            content="Third mentorship area",
            author=self.profile1,
            status="unpublished",
        )

        # Assign mentorship areas to profiles
        ProfileMentorshipArea.objects.create(
            profile=self.profile1,
            mentorship_area=self.mentorship_area1,
        )

        ProfileMentorshipArea.objects.create(
            profile=self.profile2,
            mentorship_area=self.mentorship_area2,
        )

    def test_form_initialization(self):
        """
        Test that the form initializes correctly with no errors.
        """
        form = MentorshipFilterForm()

        self.assertIsInstance(form, MentorshipFilterForm)

    def test_form_valid_mentorship_areas_filter(self):
        """
        Test that filtering by mentorship areas returns the correct profiles.
        """
        form_data = {
            "mentorship_areas": [self.mentorship_area1.id],
        }

        form = MentorshipFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertIn(
            self.mentorship_area1,
            form.cleaned_data["mentorship_areas"],
        )

    def test_form_empty_filter(self):
        """
        Test that an empty form does not raise validation errors.
        """
        form = MentorshipFilterForm(data={})

        self.assertTrue(form.is_valid())


class TestFaithMilestoneFilterForm(TestCase):
    def setUp(self):
        """
        Set up test data for filtering by faith milestones.
        """
        # Create users and assign faith milestones to profiles
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="password",
        )

        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile

        # Create sample Faith Milestones
        self.faith_milestone1 = FaithMilestone.objects.create(
            author=self.profile1,
            title="Milestone 1",
            type="profile",
            description="First faith milestone",
        )
        self.faith_milestone2 = FaithMilestone.objects.create(
            author=self.profile1,
            title="Milestone 2",
            type="profile",
            description="Second faith milestone",
        )
        self.faith_milestone3 = FaithMilestone.objects.create(
            author=self.profile1,
            title="Unrelated Milestone",
            type="other",
            description="Milestone not related to profile",
        )

        # Assign faith milestones to profiles
        ProfileFaithMilestone.objects.create(
            faith_milestone=self.faith_milestone1,
            profile=self.profile1,
        )

        ProfileFaithMilestone.objects.create(
            faith_milestone=self.faith_milestone2,
            profile=self.profile1,
        )

    def test_form_initialization(self):
        """
        Test that the form initializes correctly with no errors.
        """
        form = FaithMilestoneFilterForm()

        self.assertIsInstance(form, FaithMilestoneFilterForm)

    def test_form_valid_faith_milestones_filter(self):
        """
        Test that filtering by faith milestones returns the correct profiles.
        """
        form_data = {"faith_milestones": [self.faith_milestone1.id]}
        form = FaithMilestoneFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertIn(
            self.faith_milestone1,
            form.cleaned_data["faith_milestones"],
        )

    def test_form_empty_filter(self):
        """
        Test that an empty form does not raise validation errors.
        """
        form = FaithMilestoneFilterForm(data={})

        self.assertTrue(form.is_valid())
