"""
Tests for the forms in the `groups` app.
"""

from django.test import TestCase

from kns.custom_user.models import User
from kns.groups.models import Group
from kns.profiles.models import Profile

from ..forms import GroupBasicFilterForm, GroupForm
from . import test_constants


class TestGroupForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        self.form_data = {
            "name": "Test Group",
            "location_country": "US",
            "description": test_constants.VALID_GROUP_DESCRIPTION,
            "location_city": "New York",
            "image": None,
        }

    def test_group_form_valid(self):
        form = GroupForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_group_name_too_long(self):
        self.form_data["name"] = "A" * 51  # Exceeds the 50 character limit
        form = GroupForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_group_description_missing(self):
        self.form_data["description"] = ""
        form = GroupForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)

    def test_group_invalid_country_code(self):
        self.form_data["location_country"] = "ZZ"  # Invalid country code
        form = GroupForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("location_country", form.errors)

    def test_group_city_missing(self):
        self.form_data["location_city"] = ""
        form = GroupForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("location_city", form.errors)


class TestGroupBasicFilterForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        # Create a sample leader (Profile) for testing
        self.leader_user = User.objects.create_user(
            email="leader_user@example.com", password="password"
        )

        self.leader_profile = self.leader_user.profile

        self.leader_profile.role = "leader"
        self.leader_profile.first_name = "Larry"
        self.leader_profile.last_name = "Bond"
        self.leader_profile.is_onboarded = True

        self.leader_profile.save()

        # Create a group
        self.group = Group.objects.create(
            leader=self.leader_profile,
            name="Test Group",
            slug="test-group",
            location_country="NG",
            location_city="Bauchi",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.form_data = {
            "description": "Group related to tech",
            "location_country": "US",
            "location_city": "New York",
            "leader": "John",
        }

    def test_group_basic_filter_form_valid(self):
        form = GroupBasicFilterForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_group_description_filter(self):
        self.form_data["description"] = "Another description"

        form = GroupBasicFilterForm(data=self.form_data)

        self.assertTrue(form.is_valid())

        self.assertEqual(
            form.cleaned_data["description"],
            "Another description",
        )

    def test_group_invalid_country_code(self):
        self.form_data["location_country"] = "ZZ"

        form = GroupBasicFilterForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_group_city_filter(self):
        self.form_data["location_city"] = "San Francisco"

        form = GroupBasicFilterForm(data=self.form_data)

        self.assertTrue(form.is_valid())

        self.assertEqual(
            form.cleaned_data["location_city"],
            "San Francisco",
        )

    def test_group_leader_filter(self):
        # Set the leader name in the form data to match the test profile's name
        self.form_data["leader"] = "Larry"

        form = GroupBasicFilterForm(
            data=self.form_data,
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["leader"],
            "Larry",
        )

    def test_group_leader_missing(self):
        self.form_data["leader"] = ""

        form = GroupBasicFilterForm(
            data=self.form_data,
        )

        self.assertTrue(form.is_valid())

    def test_empty_form(self):
        form = GroupBasicFilterForm(data={})

        self.assertTrue(form.is_valid())
