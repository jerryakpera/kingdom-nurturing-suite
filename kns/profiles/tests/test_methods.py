from datetime import date
from unittest.mock import Mock

from django.test import TestCase
from django.urls import reverse

from kns.core.models import Setting
from kns.custom_user.models import User
from kns.groups.models import Group
from kns.groups.tests import factories, test_constants

from .. import methods
from ..models import ConsentForm


class ProfileMethodsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="johndoe@example.com",
            password="password123",
            verified=True,
            agreed_to_terms=True,
            is_visitor=False,
        )

        self.profile = self.user.profile

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

        self.profile.save()

        self.settings = Setting.get_or_create_setting()

    def test_get_full_name(self):
        """Test that the full name is correctly returned."""
        full_name = methods.get_full_name(self.profile)

        self.assertEqual(
            full_name,
            "John Doe",
        )

    def test_is_leading_group_false(self):
        """Test that a profile not leading a group returns False."""

        self.assertFalse(methods.is_leading_group(self.profile))

    def test_is_leading_group_true(self):
        """Test that a profile leading a group returns True."""

        # Create a group
        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.assertTrue(methods.is_leading_group(self.profile))

    def test_get_absolute_url(self):
        """Test that the correct absolute URL is returned."""
        expected_url = reverse(
            "profiles:profile_detail",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        self.assertEqual(
            methods.get_absolute_url(self.profile),
            expected_url,
        )

    def test_get_involvements_url(self):
        """Test that the correct involvements URL is returned."""
        expected_url = reverse(
            "profiles:profile_involvements",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        self.assertEqual(
            methods.get_involvements_url(self.profile),
            expected_url,
        )

    def test_get_trainings_url(self):
        """Test that the correct trainings URL is returned."""
        expected_url = reverse(
            "profiles:profile_trainings",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        self.assertEqual(
            methods.get_trainings_url(self.profile),
            expected_url,
        )

    def test_get_activities_url(self):
        """Test that the correct activities URL is returned."""
        expected_url = reverse(
            "profiles:profile_activities",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        self.assertEqual(
            methods.get_activities_url(self.profile),
            expected_url,
        )

    def test_get_settings_url(self):
        """Test that the correct settings URL is returned."""
        expected_url = reverse(
            "profiles:profile_settings",
            kwargs={
                "profile_slug": self.profile.slug,
            },
        )
        self.assertEqual(
            methods.get_settings_url(self.profile),
            expected_url,
        )

    def test_get_role_display_str_leader(self):
        """Test that the role is correctly displayed as 'Leader'."""
        role_str = methods.get_role_display_str(self.profile)
        self.assertEqual(role_str, "Leader")

    def test_get_role_display_str_external_person(self):
        """Test that a role not 'leader' or 'member' is displayed as 'External Person'."""
        self.profile.role = "visitor"
        role_str = methods.get_role_display_str(self.profile)
        self.assertEqual(role_str, "External Person")

    def test_is_eligible_to_register_group_true(self):
        """Test that an eligible profile can register a new group."""
        # Ensure no group is led by this profile
        self.assertTrue(
            methods.is_eligible_to_register_group(self.profile),
        )

    def test_is_eligible_to_register_group_false_due_to_group_led(self):
        """Test that a profile leading an existing group cannot register a new one."""
        self.profile.group_led = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.assertFalse(
            methods.is_eligible_to_register_group(self.profile),
        )

    def test_is_eligible_to_register_group_false_due_to_role(self):
        """Test that a profile without the 'leader' role cannot register a new group."""
        self.profile.role = "member"
        self.assertFalse(
            methods.is_eligible_to_register_group(self.profile),
        )

    def test_is_eligible_to_register_group_false_due_to_unverified_email(self):
        """Test that a profile with an unverified email cannot register a new group."""
        self.profile.user.verified = False
        self.assertFalse(
            methods.is_eligible_to_register_group(self.profile),
        )

    def test_is_eligible_to_register_group_false_due_to_no_agreement_to_terms(self):
        """Test that a profile that hasn't agreed to terms cannot register a new group."""
        self.profile.user.agreed_to_terms = False
        self.assertFalse(
            methods.is_eligible_to_register_group(self.profile),
        )

    def test_is_eligible_to_register_group_false_due_to_visitor_status(self):
        """Test that a profile marked as a visitor cannot register a new group."""
        self.profile.user.is_visitor = True
        self.assertFalse(
            methods.is_eligible_to_register_group(self.profile),
        )

    def test_is_eligible_to_register_group_false_due_to_incomplete_profile(self):
        """Test that a profile that is not fully completed cannot register a new group."""
        self.profile.is_profile_complete = Mock(return_value=False)
        self.assertFalse(
            methods.is_eligible_to_register_group(self.profile),
        )

    def test_is_profile_complete_true(self):
        """Test that a profile with all required fields is considered complete."""
        self.assertTrue(methods.is_profile_complete(self.profile))

    def test_is_profile_complete_false_due_to_missing_first_name(self):
        """Test that a profile with a missing first name is considered incomplete."""
        self.profile.first_name = ""
        self.assertFalse(methods.is_profile_complete(self.profile))

    def test_is_profile_complete_false_due_to_missing_last_name(self):
        """Test that a profile with a missing last name is considered incomplete."""
        self.profile.last_name = ""
        self.assertFalse(methods.is_profile_complete(self.profile))

    def test_is_profile_complete_false_due_to_missing_gender(self):
        """Test that a profile with a missing gender is considered incomplete."""
        self.profile.gender = ""
        self.assertFalse(methods.is_profile_complete(self.profile))

    def test_is_profile_complete_false_due_to_missing_date_of_birth(self):
        """Test that a profile with a missing date of birth is considered incomplete."""
        self.profile.date_of_birth = ""
        self.assertFalse(methods.is_profile_complete(self.profile))

    def test_is_profile_complete_false_due_to_missing_location_country(self):
        """Test that a profile with a missing country is considered incomplete."""
        self.profile.location_country = ""
        self.assertFalse(methods.is_profile_complete(self.profile))

    def test_is_profile_complete_false_due_to_missing_location_city(self):
        """Test that a profile with a missing city is considered incomplete."""
        self.profile.location_city = ""
        self.assertFalse(methods.is_profile_complete(self.profile))

    def test_is_profile_complete_false_due_to_missing_role(self):
        """Test that a profile with a missing role is considered incomplete."""
        self.profile.role = ""
        self.assertFalse(methods.is_profile_complete(self.profile))

    def test_is_profile_complete_false_due_to_unverified_email(self):
        """Test that a profile with an unverified email is considered incomplete."""
        self.profile.user.verified = False
        self.assertFalse(methods.is_profile_complete(self.profile))

    def test_is_profile_complete_false_due_to_no_agreement_to_terms(self):
        """Test that a profile that hasn't agreed to terms is considered incomplete."""
        self.profile.user.agreed_to_terms = False
        self.assertFalse(methods.is_profile_complete(self.profile))

    def test_get_age(self):
        """Test that the age is correctly calculated based on the date
        of birth."""
        self.profile.date_of_birth = date(1990, 1, 1)
        age = methods.get_age(self.profile)
        self.assertEqual(age, date.today().year - 1990)

    def test_get_age_none(self):
        """Test that None is returned when date of birth is not set."""
        self.profile.date_of_birth = None
        age = methods.get_age(self.profile)
        self.assertIsNone(age)

    def test_is_under_age_true(self):
        """Test that is_under_age returns True for a profile under 18
        years old."""
        self.profile.date_of_birth = date.today().replace(
            year=date.today().year - 14,
        )
        self.profile.save()

        self.assertTrue(
            methods.is_under_age(
                self.profile,
                self.settings.adult_age,
            )
        )

        self.profile.date_of_birth = None
        self.profile.save()

        self.assertTrue(
            methods.is_under_age(
                self.profile,
                self.settings.adult_age,
            )
        )

    def test_is_under_age_false(self):
        """Test that is_under_age returns False for a profile 18
        years or older."""
        self.profile.date_of_birth = date.today().replace(
            year=date.today().year - 18,
        )
        self.assertFalse(
            methods.is_under_age(
                self.profile,
                self.settings.adult_age,
            )
        )

    def test_get_current_consent_form_exists(self):
        """Test that the current consent form is returned when it exists."""
        # Create a ConsentForm instance associated with the profile
        consent_form = ConsentForm.objects.create(
            profile=self.profile,
            submitted_by=self.profile,
        )

        # Assign the ConsentForm instance to the profile
        self.profile.consent_form = consent_form

        # Call the method to test
        result = methods.get_current_consent_form(self.profile)

        # Assert that the returned consent form is the one we created
        self.assertEqual(result, consent_form)

    def test_get_current_consent_form_none(self):
        """Test that None is returned when there is no consent form."""
        self.profile.consent_form = None
        consent_form = methods.get_current_consent_form(self.profile)
        self.assertIsNone(consent_form)

    def test_can_become_leader_role_false_due_to_incomplete_profile(self):
        """Test that a profile cannot become a leader if the
        profile is incomplete."""
        self.profile.is_profile_complete = Mock(
            return_value=False,
        )
        self.assertFalse(methods.can_become_leader_role(self.profile))

    def test_can_become_leader_role_false_due_to_already_being_leader(self):
        """Test that a profile cannot become a leader if the profile
        already has the leader role."""
        self.profile.is_profile_complete = Mock(
            return_value=True,
        )
        self.profile.role = "leader"
        self.assertFalse(methods.can_become_leader_role(self.profile))

    def test_can_become_leader_role_false_due_to_needing_consent_form(self):
        """Test that a profile cannot become a leader if the profile
        needs a consent form."""
        self.profile.is_profile_complete = Mock(return_value=True)
        self.profile.role = "member"
        self.profile.needs_consent_form = Mock(return_value=True)
        self.assertFalse(methods.can_become_leader_role(self.profile))

    def test_can_become_leader_role_true(self):
        """Test that a profile can become a leader if all conditions
        are met."""
        self.profile.is_profile_complete = Mock(return_value=True)
        self.profile.role = "member"
        self.profile.needs_consent_form = Mock(return_value=False)
        self.assertTrue(methods.can_become_leader_role(self.profile))

    def test_can_become_member_role_false_due_to_incomplete_profile(self):
        """
        Test that a profile cannot become a member if the profile
        is incomplete.
        """

        self.profile.is_profile_complete = Mock(return_value=False)

        self.profile.role = "leader"
        self.profile.needs_consent_form = Mock(return_value=False)

        self.assertFalse(methods.can_become_member_role(self.profile))

    def test_can_become_member_role_false_due_to_already_being_member(self):
        """
        Test that a profile cannot become a member if the profile
        is already a member.
        """

        self.profile.is_profile_complete = Mock(return_value=True)

        self.profile.role = "member"
        self.profile.needs_consent_form = Mock(return_value=False)

        self.assertFalse(methods.can_become_member_role(self.profile))

    def test_can_become_member_role_false_due_to_needing_consent_form(self):
        """
        Test that a profile cannot become a member if the profile
        needs a consent form.
        """

        self.profile.is_profile_complete = Mock(return_value=True)

        self.profile.role = "leader"
        self.profile.needs_consent_form = Mock(return_value=True)

        self.assertFalse(methods.can_become_member_role(self.profile))

    def test_can_become_member_role_false_due_to_leading_group(self):
        """
        Test that a profile cannot become a member if the profile is
        leading a group.
        """
        self.profile.is_profile_complete = Mock(return_value=True)

        self.profile.role = "leader"

        factories.GroupFactory(
            name="Bible Study Group",
            location_country="Nigeria",
            location_city="Lagos",
            leader=self.profile,
        )

        self.profile.needs_consent_form = Mock(return_value=False)

        self.profile.is_leading_group = Mock(return_value=True)
        self.assertFalse(methods.can_become_member_role(self.profile))

    def test_can_become_member_role_true(self):
        """
        Test that a profile can become a member if all conditions
        are met.
        """

        self.profile.is_profile_complete = Mock(return_value=True)

        self.profile.role = "leader"
        self.profile.needs_consent_form = Mock(return_value=False)

        self.profile.is_leading_group = Mock(return_value=False)

        group_leader_user = User.objects.create(
            email="groupleader@example.com",
            password="password",
        )

        group = factories.GroupFactory(
            name="Bible Study Group",
            location_country="Nigeria",
            location_city="Lagos",
            leader=group_leader_user.profile,
        )

        group.add_member(self.profile)

        self.assertTrue(methods.can_become_member_role(self.profile))
