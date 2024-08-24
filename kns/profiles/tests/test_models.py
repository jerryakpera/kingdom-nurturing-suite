from datetime import date, timedelta
from unittest.mock import patch

import pytest
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from kns.core.models import Setting
from kns.custom_user.models import User
from kns.groups.models import Group
from kns.groups.tests import test_constants
from kns.profiles.models import ConsentForm, Profile


class TestProfileModel(TestCase):
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

    # def test_profile_is_leading_group(self):
    #     """
    #     Test that the is_leading_group method correctly identifies if
    #     the profile is leading a group.
    #     """
    #     self.profile.first_name = "John"
    #     self.profile.last_name = "Doe"
    #     self.profile.gender = "Male"
    #     self.profile.date_of_birth = "1990-01-01"
    #     self.profile.place_of_birth_country = "USA"
    #     self.profile.place_of_birth_city = "New York"
    #     self.profile.location_country = "USA"
    #     self.profile.location_city = "New York"
    #     self.profile.role = "leader"
    #     self.profile.slug = "john-doe"

    #     self.user.verified = True
    #     self.user.agreed_to_terms = True

    #     self.profile.save()
    #     self.user.save()

    #     Group.objects.create(
    #         leader=self.profile,
    #         name="Test Group",
    #         slug="test-group",
    #         description=test_constants.VALID_GROUP_DESCRIPTION,
    #     )

    #     assert self.profile.is_leading_group()

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

    def test_profile_is_leading_group(self):
        """
        Test that the __str__ method returns the full name of the profile.
        """
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.gender = "Male"
        self.profile.date_of_birth = "1990-01-01"
        self.profile.place_of_birth_country = "USA"
        self.profile.place_of_birth_city = "New York"
        self.profile.location_country = "USA"
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

    def test_get_absolute_url(self):
        expected_url = reverse(
            "profiles:profile_detail",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        self.assertEqual(
            self.profile.get_absolute_url(),
            expected_url,
        )

    def test_get_involvements_url(self):
        expected_url = reverse(
            "profiles:profile_involvements",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )

        self.assertEqual(
            self.profile.get_involvements_url(),
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

    # Add more tests as needed, for example:
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
