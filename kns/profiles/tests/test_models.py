import time
from datetime import date, timedelta

import pytest
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from kns.core.models import Setting
from kns.custom_user.models import User
from kns.discipleships.models import Discipleship
from kns.groups.models import Group
from kns.groups.tests import test_constants
from kns.mentorships.models import MentorshipArea, ProfileMentorshipArea
from kns.onboarding.models import ProfileCompletion, ProfileCompletionTask
from kns.profiles.models import (
    ConsentForm,
    EncryptionReason,
    Profile,
    ProfileEncryption,
)
from kns.skills.models import ProfileInterest, ProfileSkill, Skill
from kns.vocations.models import ProfileVocation, Vocation


class TestProfileModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """

        User.objects.all().delete()
        Profile.objects.all().delete()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.settings = Setting.get_or_create_setting()

    def test_profile_creation_on_user_creation(self):
        """
        Test that a Profile instance is created when a User instance is created.
        """
        profile = Profile.objects.get(user=self.user)

        assert profile is not None
        assert profile.email == self.user.email

    def test_profile_get_role_display_str(self):
        """
        Test that the get_role_display_str method returns the correct
        string representation for the profile's role.
        """
        # Test when role is "member"
        self.profile.role = "member"
        self.profile.save()

        assert self.profile.get_role_display_str() == "Member"

        # Test when role is "leader"
        self.profile.role = "leader"
        self.profile.save()

        assert self.profile.get_role_display_str() == "Leader"

        # Test when role is "external_person"
        self.profile.role = "external_person"
        self.profile.save()

        assert self.profile.get_role_display_str() == "External Person"

    def test_profile_is_leading_group(self):
        """
        Test that the is_leading_group method correctly identifies if
        the profile is leading a group.
        """
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.gender = "Male"
        self.profile.date_of_birth = "1990-01-01"
        self.profile.place_of_birth_country = "US"
        self.profile.place_of_birth_city = "New York"
        self.profile.location_country = "US"
        self.profile.location_city = "New York"
        self.profile.role = "leader"
        self.profile.slug = "john-doe"

        self.user.verified = True
        self.user.agreed_to_terms = True

        self.profile.save()
        self.user.save()

        Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        assert self.profile.is_leading_group()

    def test_profile_get_age(self):
        """
        Test that the get_age method returns the correct age based on
        date_of_birth.
        """
        self.profile.date_of_birth = date(1990, 1, 1)
        self.profile.save()

        expected_age = timezone.now().year - 1990
        if (timezone.now().month, timezone.now().day) < (1, 1):
            expected_age -= (
                1  # Adjust age if the birthday hasn't occurred yet this year
            )

        assert self.profile.get_age() == expected_age

    def test_profile_is_under_age(self):
        """
        Test that the is_under_age method returns the correct under
        age status.
        """

        # Test with a date of birth that should be under age
        self.profile.date_of_birth = date(2015, 1, 1)
        self.profile.save()

        self.user.refresh_from_db()
        assert self.profile.is_under_age()

        # Test with a date of birth that should not be under age
        self.profile.date_of_birth = date(1985, 1, 1)
        self.profile.save()

        assert not self.profile.is_under_age()

    def test_profile_get_current_consent_form(self):
        """
        Test that the get_current_consent_form method returns the
        correct consent form.
        """
        consent_form = ConsentForm.objects.create(
            submitted_by=self.profile,
            profile=self.profile,
        )

        assert self.profile.get_current_consent_form() is not None
        assert consent_form.profile == self.profile

    def test_profile_needs_consent_form(self):
        """
        Test that the needs_consent_form method returns the correct need
        for a consent form.
        """
        # Test with a date of birth that should not require a consent form
        self.profile.date_of_birth = date(1990, 1, 1)
        self.profile.save()

        # Assert that a consent form is needed
        self.assertFalse(self.profile.needs_consent_form())

        # Test with a date of birth that should require a consent form
        self.profile.date_of_birth = date.today() - timedelta(
            days=365 * (self.settings.adult_age - 1)
        )  # Just below adult age
        self.profile.save()

        # Assert that a consent form is needed
        self.assertTrue(self.profile.needs_consent_form())

        # Create and associate a consent form
        self.consent_form = ConsentForm.objects.create(
            profile=self.profile,
            submitted_by=self.profile,
        )

        # Assert that a consent form is still needed before approval
        self.assertTrue(self.profile.needs_consent_form())

        # Approve the consent form
        self.consent_form.approve(self.profile)

        # Assert that no further consent form is needed after approval
        self.assertFalse(self.profile.needs_consent_form())

        # Approve the consent form
        self.consent_form.reject(self.profile)

        # Assert that consent form is needed after rejection
        self.assertTrue(self.profile.needs_consent_form())

    def test_profile_email_unique_constraint(self):
        """
        Test that the email field on the Profile model is unique.
        """
        User.objects.create_user(
            email="uniqueuser@example.com",
            password="testpassword",
        )

        with pytest.raises(IntegrityError) as excinfo:
            User.objects.create_user(
                email="uniqueuser@example.com", password="anotherpassword"
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_profile_created_at_exists(self):
        """
        Test that the created_at field exists on the profile instance.
        """
        assert self.profile.created_at is not None

    def test_profile_updated_at_exists(self):
        """
        Test that the updated_at field exists on the profile instance.
        """
        assert self.profile.updated_at is not None

    def test_profile_role_exists(self):
        """
        Test that the role field exists on the profile instance.
        """
        assert self.profile.role is not None
        assert self.profile.role in [
            "member",
            "leader",
            "external_person",
        ]

    def test_profile_str_method(self):
        """
        Test that the __str__ method returns the full name of the
        profile.
        """
        self.profile.last_name = "Doe"
        self.profile.first_name = "John"

        self.profile.save()

        assert str(self.profile) == "John Doe"

    def test_get_absolute_url(self):
        expected_url = reverse(
            "profiles:profile_overview",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        self.assertEqual(
            self.profile.get_absolute_url(),
            expected_url,
        )

    def test_get_trainings_url(self):
        expected_url = reverse(
            "profiles:profile_trainings",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        self.assertEqual(
            self.profile.get_trainings_url(),
            expected_url,
        )

    def test_get_activities_url(self):
        expected_url = reverse(
            "profiles:profile_activities",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        self.assertEqual(
            self.profile.get_activities_url(),
            expected_url,
        )

    def test_get_settings_url(self):
        expected_url = reverse(
            "profiles:profile_settings",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        self.assertEqual(
            self.profile.get_settings_url(),
            expected_url,
        )

    def test_get_mentorships_url(self):
        expected_url = reverse(
            "profiles:profile_mentorships",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        self.assertEqual(
            self.profile.get_mentorships_url(),
            expected_url,
        )

    def test_get_discipleships_url(self):
        expected_url = reverse(
            "profiles:profile_discipleships",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        self.assertEqual(
            self.profile.get_discipleships_url(),
            expected_url,
        )

    def test_get_role_display_str(self):
        self.profile.role = "external_person"

        self.assertEqual(
            self.profile.get_role_display_str(),
            "External Person",
        )

    def test_is_eligible_to_register_group(self):
        # Set up necessary data and mock methods as needed
        self.profile.is_mentor = True
        self.profile.is_skill_training_facilitator = True
        self.profile.is_movement_training_facilitator = True

        self.profile.save()

        # Assuming that the eligibility depends on certain criteria
        self.assertFalse(self.profile.is_eligible_to_register_group())

    def test_is_profile_complete(self):
        # Assuming that profile completeness depends on having a
        # first name and last name
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.save()

        self.assertFalse(self.profile.is_profile_complete())

    def test_can_become_leader_role_true(self):
        """
        Test that the can_become_member_role method returns True when the
        profile is eligible to become a member.
        """
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.gender = "Male"
        self.profile.date_of_birth = date(1990, 1, 1)
        self.profile.place_of_birth_country = "US"
        self.profile.place_of_birth_city = "New York"
        self.profile.location_country = "US"
        self.profile.location_city = "New York"
        self.profile.role = "member"
        self.profile.slug = "john-doe"

        self.profile.save()

        self.profile.user.verified = True
        self.profile.user.agreed_to_terms = True

        assert self.profile.can_become_leader_role() is True

    def test_can_become_external_person_role_true(self):
        """
        Test that the can_become_member_role method returns True when the
        profile is eligible to become a member.
        """
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.gender = "Male"
        self.profile.date_of_birth = date(1990, 1, 1)
        self.profile.place_of_birth_country = "US"
        self.profile.place_of_birth_city = "New York"
        self.profile.location_country = "US"
        self.profile.location_city = "New York"
        self.profile.role = "member"
        self.profile.slug = "john-doe"

        self.profile.save()

        self.profile.user.verified = True
        self.profile.user.agreed_to_terms = True

        assert self.profile.can_become_external_person_role() is True

    def test_can_become_member_role_true(self):
        """
        Test that the can_become_member_role method returns True when the
        profile is eligible to become a member.
        """
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.gender = "Male"
        self.profile.date_of_birth = date(1990, 1, 1)
        self.profile.place_of_birth_country = "US"
        self.profile.place_of_birth_city = "New York"
        self.profile.location_country = "US"
        self.profile.location_city = "New York"
        self.profile.role = "leader"
        self.profile.slug = "john-doe"

        self.profile.save()

        self.profile.user.verified = True
        self.profile.user.agreed_to_terms = True

        assert self.profile.can_become_member_role() is True

    def test_can_become_member_role_unverified(self):
        """
        Test that the can_become_member_role method returns False when the
        profile is not verified.
        """
        # Set up the profile with unverified status
        self.profile.is_verified = False
        self.profile.is_under_age = False
        self.profile.is_banned = False

        self.profile.save()

        assert self.profile.can_become_member_role() is False

    def test_can_become_member_role_under_age(self):
        """
        Test that the can_become_member_role method returns False when the
        profile is under age.
        """
        # Set up the profile as under age
        self.profile.is_verified = True
        self.profile.is_under_age = True
        self.profile.is_banned = False

        self.profile.save()

        assert self.profile.can_become_member_role() is False

    def test_get_full_name_no_encryption(self):
        """
        Test that the get_full_name method returns the full name
        of the profile instance when there is no ProfileEncryption.
        """
        # Set first and last name on the profile
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.save()

        # Test get_full_name with no encryption
        self.assertEqual(
            self.profile.get_full_name(),
            "John Doe",
        )

    def test_get_full_name_with_encryption(self):
        """
        Test that the get_full_name method returns the full name
        of the profile instance when there is a ProfileEncryption.
        """
        EncryptionReason.objects.create(
            title="Sample encryption reason title",
            description="Sample encryption reason description",
            author=self.profile,
        )

        # Create ProfileEncryption instance
        ProfileEncryption.objects.create(
            profile=self.profile,
            first_name="Jane",
            last_name="Smith",
            encryption_reason=EncryptionReason.objects.first(),
        )

        # Test get_full_name with encryption
        self.assertEqual(
            self.profile.get_full_name(),
            "Jane Smith",
        )

    def test_get_full_name_with_encryption_and_no_profile(self):
        """
        Test that the get_full_name method returns the profile's full name
        if the profile encryption is not present.
        """
        # Set first and last name on the profile
        self.profile.first_name = "Emily"
        self.profile.last_name = "Davis"

        self.profile.save()

        # Test get_full_name with no encryption
        self.assertEqual(
            self.profile.get_full_name(),
            "Emily Davis",
        )

        EncryptionReason.objects.create(
            title="Sample encryption reason title",
            description="Sample encryption reason description",
            author=self.profile,
        )

        # Create ProfileEncryption instance
        ProfileEncryption.objects.create(
            profile=self.profile,
            first_name="Emma",
            last_name="Brown",
            encryption_reason=EncryptionReason.objects.first(),
        )

        # Test get_full_name with encryption
        self.assertEqual(
            self.profile.get_full_name(),
            "Emma Brown",
        )

    def test_get_real_name(self):
        """
        Test that the get_real_name method returns the real name
        of the profile instance when there is no ProfileEncryption.
        """
        # Set first and last name on the profile
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.save()

        # Test get_real_name with no encryption
        self.assertEqual(
            self.profile.get_real_name(),
            "John Doe",
        )

    def test_phone_display_no_phone(self):
        """
        Test that the phone_display method returns the phone number of the
        profile.
        """
        self.assertEqual(
            self.profile.phone_display(),
            "---",
        )

    def test_phone_display(self):
        """
        Test that the phone_display method returns the phone number of the
        profile.
        """

        self.profile.phone_prefix = "234"
        self.profile.phone = "8122151744"

        self.assertEqual(
            self.profile.phone_display(),
            "(+234) 8122151744",
        )

    def test_get_vocations_as_string(self):
        """
        Test that the get_vocations_as_string method returns the vocations
        as a comma-separated string.
        """

        # Create some sample vocations
        vocation1 = Vocation.objects.create(
            title="Teacher",
            description="Sample description for a vocation",
            author=self.profile,
        )
        vocation2 = Vocation.objects.create(
            title="Engineer",
            description="Sample description for a vocation",
            author=self.profile,
        )

        # Initially, the profile should have no vocations
        self.assertEqual(self.profile.get_vocations_as_string(), "No vocations")

        profile_vocation1 = ProfileVocation.objects.create(
            profile=self.profile,
            vocation=vocation1,
        )

        profile_vocation2 = ProfileVocation.objects.create(
            profile=self.profile,
            vocation=vocation2,
        )

        # Test that the vocations are returned as a comma-separated string
        self.assertEqual(
            self.profile.get_vocations_as_string(),
            "Teacher, Engineer",
        )

        # Remove vocations and test that the method returns "No vocations"
        profile_vocation1.delete()
        profile_vocation2.delete()

        self.assertEqual(
            self.profile.get_vocations_as_string(),
            "No vocations",
        )

    def test_get_mentorship_areas_as_str_no_areas(self):
        """
        Test that get_mentorship_areas_as_str returns '---' when there are no mentorship areas.
        """
        assert self.profile.get_mentorship_areas_as_str() == "---"

    def test_get_mentorship_areas_as_str_with_one_area(self):
        """
        Test that get_mentorship_areas_as_str returns the title of the mentorship area
        when there is one mentorship area.
        """
        area = MentorshipArea.objects.create(
            title="Software Engineering",
            content="Mentorship on software engineering topics",
            author=self.profile,
        )

        ProfileMentorshipArea.objects.create(
            profile=self.profile,
            mentorship_area=area,
        )

        assert self.profile.get_mentorship_areas_as_str() == "Software Engineering"

    def test_get_mentorship_areas_as_str_with_multiple_areas(self):
        """
        Test that get_mentorship_areas_as_str returns a comma-separated string
        of mentorship area titles when there are multiple mentorship areas.
        """
        area1 = MentorshipArea.objects.create(
            title="Software Engineering",
            content="Mentorship on software engineering topics",
            author=self.profile,
        )

        area2 = MentorshipArea.objects.create(
            title="Data Science",
            content="Mentorship on data science topics",
            author=self.profile,
        )

        ProfileMentorshipArea.objects.create(
            profile=self.profile,
            mentorship_area=area1,
        )

        ProfileMentorshipArea.objects.create(
            profile=self.profile,
            mentorship_area=area2,
        )

        expected_result = "Software Engineering, Data Science"

        assert self.profile.get_mentorship_areas_as_str() == expected_result

    def test_change_role_to_leader(self):
        """
        Test that the change_role_to_leader method changes the profile's role to 'leader'.
        """
        self.profile.role = "member"
        self.profile.save()

        self.profile.change_role_to_leader()
        self.profile.refresh_from_db()

        assert self.profile.role == "leader"

    def test_change_role_to_member(self):
        """
        Test that the change_role_to_member method changes the profile's role to 'member'.
        """
        self.profile.role = "leader"
        self.profile.save()

        self.profile.change_role_to_member()
        self.profile.refresh_from_db()

        assert self.profile.role == "member"

    def test_change_role_to_external_person(self):
        """
        Test that the change_role_to_external_person method changes the
        profile's role to 'external_person'.
        """
        self.profile.role = "leader"
        self.profile.save()

        self.profile.change_role_to_external_person()
        self.profile.refresh_from_db()

        assert self.profile.role == "external_person"

    def test_formatted_date_of_birth_with_date(self):
        """
        Test that the formatted_date_of_birth method returns the correct
        formatted date when a date is set.
        """
        self.profile.date_of_birth = date(1990, 5, 15)
        self.profile.save()

        expected_output = "May 15, 1990"
        assert self.profile.formatted_date_of_birth() == expected_output

    def test_formatted_date_of_birth_without_date(self):
        """
        Test that the formatted_date_of_birth method returns '---' when no date of birth is set.
        """
        self.profile.date_of_birth = None
        self.profile.save()

        assert self.profile.formatted_date_of_birth() == "---"

    def test_place_of_birth_display_with_country_and_city(self):
        """
        Test that the place_of_birth_display method returns a formatted
        string with both country and city.
        """
        self.profile.place_of_birth_country = "US"
        self.profile.place_of_birth_city = "New York"
        self.profile.save()

        expected_output = "United States of America, New York"
        assert self.profile.place_of_birth_display() == expected_output

    def test_place_of_birth_display_with_only_country(self):
        """
        Test that the place_of_birth_display method returns only the country
        if the city is not set.
        """
        self.profile.place_of_birth_country = "US"
        self.profile.place_of_birth_city = None
        self.profile.save()

        expected_output = "United States of America"
        assert self.profile.place_of_birth_display() == expected_output

    def test_place_of_birth_display_without_country_and_city(self):
        """
        Test that the place_of_birth_display method returns '---' if
        neither country nor city is set.
        """
        self.profile.place_of_birth_country = None
        self.profile.place_of_birth_city = None
        self.profile.save()

        assert self.profile.place_of_birth_display() == "---"

    def test_location_display_with_country_and_city(self):
        """
        Test that the location_display method returns a formatted string
        with both country and city.
        """
        self.profile.location_country = "US"
        self.profile.location_city = "Los Angeles"
        self.profile.save()

        expected_output = "United States of America, Los Angeles"
        assert self.profile.location_display() == expected_output

    def test_location_display_with_only_country(self):
        """
        Test that the location_display method returns only the country if the city is not set.
        """
        self.profile.location_country = "US"
        self.profile.location_city = None
        self.profile.save()

        expected_output = "United States of America"
        assert self.profile.location_display() == expected_output

    def test_location_display_without_country_and_city(self):
        """
        Test that the location_display method returns '---' if neither country nor city is set.
        """
        self.profile.location_country = None
        self.profile.location_city = None
        self.profile.save()

        assert self.profile.location_display() == "---"


class TestConsentFormModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """
        User.objects.all().delete()
        Profile.objects.all().delete()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )
        self.profile = self.user.profile

    def test_consent_form_str_pending(self):
        """
        Test the __str__ method when the consent form is pending.
        """
        consent_form = ConsentForm.objects.create(
            profile=self.profile, submitted_by=self.profile, status=ConsentForm.PENDING
        )

        expected_str = (
            f"{self.profile} consent form - {consent_form.get_status_display()}"
        )
        assert str(consent_form) == expected_str

    def test_consent_form_str_approved(self):
        """
        Test the __str__ method when the consent form is approved.
        """
        consent_form = ConsentForm.objects.create(
            profile=self.profile, submitted_by=self.profile, status=ConsentForm.APPROVED
        )

        expected_str = (
            f"{self.profile} consent form - {consent_form.get_status_display()}"
        )
        assert str(consent_form) == expected_str

    def test_consent_form_str_rejected(self):
        """
        Test the __str__ method when the consent form is rejected.
        """
        consent_form = ConsentForm.objects.create(
            profile=self.profile, submitted_by=self.profile, status=ConsentForm.REJECTED
        )

        expected_str = (
            f"{self.profile} consent form - {consent_form.get_status_display()}"
        )
        assert str(consent_form) == expected_str


class TestEncryptionReasonModel(TestCase):
    def setUp(self):
        # Create a sample profile instance for the ForeignKey relationship
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )

        self.profile = self.user.profile

        self.encryption_reason = EncryptionReason.objects.create(
            title="Sample Encryption Title",
            slug="sample-encryption-title",
            description="Sample description for encryption reason",
            author=self.profile,
        )

    def test_str_method(self):
        # Test the __str__ method of EncryptionReason
        self.assertEqual(
            str(self.encryption_reason),
            "Sample Encryption Title",
        )


class TestProfileEncryptionModel(TestCase):
    def setUp(self):
        # Create instances for testing
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )

        self.profile = self.user.profile

        self.encryption_reason = EncryptionReason.objects.create(
            title="Sample Encryption Title",
            slug="sample-encryption-title",
            description="Sample description for encryption reason",
            author=self.profile,
        )
        self.profile_encryption = ProfileEncryption.objects.create(
            profile=self.profile,
            first_name="Emma",
            last_name="Brown",
            encryption_reason=self.encryption_reason,
        )

    def test_str_method(self):
        # Test the __str__ method of ProfileEncryption
        expected_str = f"{self.profile.get_full_name()} encrypted as Emma Brown"

        self.assertEqual(str(self.profile_encryption), expected_str)


class TestDiscipleshipModel(TestCase):
    def setUp(self):
        """
        Setup method to create necessary profiles for testing.
        """
        self.user1 = User.objects.create_user(
            email="testuser1@example.com",
            password="testpassword",
        )
        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="testpassword",
        )
        self.user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="testpassword",
        )

        self.disciple = self.user1.profile
        self.discipler = self.user2.profile

        self.author = self.user3.profile

    def test_discipleship_creation(self):
        """
        Test that a Discipleship instance is created correctly.
        """
        discipleship = Discipleship.objects.create(
            disciple=self.disciple,
            discipler=self.discipler,
            group="Group leader",
            author=self.author,
        )

        self.assertIsNotNone(discipleship)
        self.assertEqual(discipleship.disciple, self.disciple)
        self.assertEqual(discipleship.discipler, self.discipler)
        self.assertEqual(discipleship.group, "Group leader")
        self.assertEqual(discipleship.author, self.author)

    def test_discipleship_slug_creation(self):
        """
        Test that the slug is automatically generated for a Discipleship instance.
        """
        discipleship = Discipleship.objects.create(
            disciple=self.disciple,
            discipler=self.discipler,
            group="group_member",
            author=self.author,
        )

        self.assertIsNotNone(discipleship.slug)
        self.assertEqual(
            Discipleship.objects.filter(slug=discipleship.slug).count(),
            1,
        )

    def test_discipleship_str_method(self):
        """
        Test that the __str__ method returns the correct string representation.
        """
        discipleship = Discipleship.objects.create(
            disciple=self.disciple,
            discipler=self.discipler,
            group="Group leader",
            author=self.author,
        )
        expected_str = (
            f"Group leader discipleship of {self.disciple} by {self.discipler}"
        )
        self.assertEqual(
            str(discipleship),
            expected_str,
        )

    def test_discipleship_ordering(self):
        """
        Test that the Discipleship instances are ordered by created_at in descending order.
        """
        Discipleship.objects.create(
            disciple=self.user1.profile,
            discipler=self.user2.profile,
            group="group_member",
            author=self.author,
        )

        # Add a delay to ensure a different timestamp
        time.sleep(0.01)

        discipleship2 = Discipleship.objects.create(
            disciple=self.user2.profile,
            discipler=self.user3.profile,
            group="first_12",
            author=self.author,
        )

        discipleships = Discipleship.objects.all()

        self.assertEqual(discipleships[0], discipleship2)

    def test_group_display(self):
        discipleship = Discipleship.objects.create(
            disciple=self.user2.profile,
            discipler=self.user3.profile,
            group="first_12",
            author=self.author,
        )

        self.assertTrue(discipleship.group_display(), "First 12")


class TestProfileCompletionTasks(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """
        super().setUp()

        User.objects.all().delete()

        Profile.objects.all().delete()
        ProfileCompletion.objects.all().delete()
        ProfileCompletionTask.objects.all().delete()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

    def test_create_profile_completion_tasks_for_leader(self):
        """
        Test that the correct tasks are created for a profile with the role of 'leader'.
        """
        self.profile.role = "leader"
        self.profile.save()

        self.profile.create_profile_completion_tasks()

        # Verify ProfileCompletion entry creation
        profile_completion = ProfileCompletion.objects.get(
            profile=self.profile,
        )

        assert profile_completion is not None

        # Verify the creation of tasks
        tasks = [
            "register_group",
            "register_first_member",
            "add_vocations_skills",
            "browse_events",
        ]

        for task_name in tasks:
            task = ProfileCompletionTask.objects.filter(
                profile=self.profile, task_name=task_name
            )
            assert task.exists()

    def test_create_profile_completion_tasks_for_non_leader(self):
        """
        Test that the correct tasks are created for a profile with a role other than 'leader'.
        """
        self.profile.role = "member"
        self.profile.save()

        self.profile.create_profile_completion_tasks()

        # Verify ProfileCompletion entry creation
        profile_completion = ProfileCompletion.objects.get(profile=self.profile)
        assert profile_completion is not None

        # Verify the creation of tasks
        tasks = [
            "add_vocations_skills",
            "browse_events",
        ]

        for task_name in tasks:
            task = ProfileCompletionTask.objects.filter(
                profile=self.profile,
                task_name=task_name,
            )

            assert task.exists()

        # Verify that 'register_group' task is not created
        register_group_task = ProfileCompletionTask.objects.filter(
            profile=self.profile, task_name="register_group"
        )

        assert not register_group_task.exists()

    def test_create_profile_completion_tasks_no_duplicates(self):
        """
        Test that duplicate tasks are not created if they already exist.
        """
        self.profile.role = "leader"
        self.profile.save()

        # Create tasks for the first time
        self.profile.create_profile_completion_tasks()

        # Create tasks again to test for duplicates
        self.profile.create_profile_completion_tasks()

        # Verify the number of tasks is correct
        tasks = [
            "register_group",
            "register_first_member",
            "add_vocations_skills",
            "browse_events",
        ]

        for task_name in tasks:
            task_count = ProfileCompletionTask.objects.filter(
                profile=self.profile, task_name=task_name
            ).count()

            assert task_count == 1

    def test_profile_completion_entry_creation(self):
        """
        Test that a ProfileCompletion entry is created when tasks are created.
        """
        self.profile.create_profile_completion_tasks()

        profile_completion = ProfileCompletion.objects.filter(
            profile=self.profile,
        ).exists()

        assert profile_completion is True


class TestCheckAndCompleteVocationsSkills(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """
        # Clean up existing data to ensure a clean test environment
        # User.objects.all().delete()
        # Profile.objects.all().delete()
        # ProfileSkill.objects.all().delete()
        # ProfileInterest.objects.all().delete()
        # ProfileVocation.objects.all().delete()
        # ProfileCompletionTask.objects.all().delete()

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.profile = self.user.profile

        self.profile.role = "leader"
        self.profile.save()

        self.profile.create_profile_completion_tasks()

        # Create Skill and Vocation instances
        self.skill = Skill.objects.create(
            title="Python Programming",
            content="<p>Advanced Python programming skills.</p>",
            author=self.profile,
        )

        self.interest = Skill.objects.create(
            title="Interest in Python",
            content="<p>Interest in learning Python programming.</p>",
            author=self.profile,
        )

        self.vocation = Vocation.objects.create(
            title="Software Developer",
            description="Develops software.",
            author=self.profile,
        )

    def test_all_items_present_task_not_completed(self):
        """
        Test when the profile has all required items but the task is not completed.
        """
        ProfileSkill.objects.create(
            profile=self.profile,
            skill=self.skill,
        )
        ProfileInterest.objects.create(
            profile=self.profile,
            interest=self.interest,
        )
        ProfileVocation.objects.create(
            profile=self.profile,
            vocation=self.vocation,
        )

        self.profile.check_and_complete_vocations_skills()

        task = ProfileCompletionTask.objects.get(
            profile=self.profile, task_name="add_vocations_skills"
        )
        self.assertTrue(task.is_complete)

    def test_all_items_present_task_already_completed(self):
        """
        Test when the profile has all required items but the task is already completed.
        """
        ProfileSkill.objects.create(
            profile=self.profile,
            skill=self.skill,
        )
        ProfileInterest.objects.create(
            profile=self.profile,
            interest=self.interest,
        )
        ProfileVocation.objects.create(
            profile=self.profile,
            vocation=self.vocation,
        )

        task = ProfileCompletionTask.objects.get(
            profile=self.profile,
            task_name="add_vocations_skills",
        )

        task.is_complete = True
        task.save()

        self.profile.check_and_complete_vocations_skills()

        task = ProfileCompletionTask.objects.get(
            profile=self.profile,
            task_name="add_vocations_skills",
        )

        self.assertTrue(task.is_complete)

    def test_missing_items(self):
        """
        Test when the profile is missing one or more required items.
        """
        self.profile.check_and_complete_vocations_skills()

        task_exists = ProfileCompletionTask.objects.filter(
            profile=self.profile,
            task_name="add_vocations_skills",
        ).exists()

        task = ProfileCompletionTask.objects.get(
            profile=self.profile,
            task_name="add_vocations_skills",
        )

        self.assertTrue(task_exists)
        self.assertFalse(task.is_complete)
