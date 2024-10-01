from django.test import TestCase

from kns.custom_user.models import User
from kns.groups.models import Group
from kns.groups.tests import test_constants

from ..forms import DiscipleshipFilterForm, GroupMemberDiscipleForm


class TestGroupMemberDiscipleForm(TestCase):
    def setUp(self):
        """
        Set up users, profiles, and groups for testing.
        """
        # Create users and their profiles
        self.user1 = User.objects.create_user(
            email="leader@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="member1@example.com",
            password="password",
        )
        self.user3 = User.objects.create_user(
            email="member2@example.com",
            password="password",
        )

        self.user1.verified = True
        self.user1.agreed_to_terms = True
        self.user1.save()

        self.user2.verified = True
        self.user2.agreed_to_terms = True
        self.user2.save()

        self.user3.verified = True
        self.user3.agreed_to_terms = True
        self.user3.save()

        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.profile3 = self.user3.profile

        # Create a group
        self.group = Group.objects.create(
            leader=self.profile1,
            name="Test Group",
            slug="test-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.group.add_member(self.profile2)
        self.group.add_member(self.profile3)

    def test_form_initial_queryset(self):
        """
        Test that the form's disciple queryset is correctly filtered
        based on the profile's group members.
        """
        form = GroupMemberDiscipleForm(
            profile=self.profile1,
        )

        self.assertIn(
            self.profile2,
            form.fields["disciple"].queryset,
        )
        self.assertIn(
            self.profile3,
            form.fields["disciple"].queryset,
        )

    def test_form_excludes_unverified_profiles(self):
        """
        Test that unverified profiles are excluded from the queryset.
        """
        self.user2.verified = False
        self.user2.save()

        form = GroupMemberDiscipleForm(profile=self.profile1)

        self.assertNotIn(self.profile2, form.fields["disciple"].queryset)
        self.assertIn(self.profile3, form.fields["disciple"].queryset)

    def test_form_excludes_profiles_not_agreed_to_terms(self):
        """
        Test that profiles that have not agreed to terms are excluded
        from the queryset.
        """
        self.user3.agreed_to_terms = False
        self.user3.save()

        form = GroupMemberDiscipleForm(profile=self.profile1)

        self.assertIn(self.profile2, form.fields["disciple"].queryset)
        self.assertNotIn(self.profile3, form.fields["disciple"].queryset)

    def test_form_valid_data(self):
        """
        Test that the form is valid with correct data.
        """
        form_data = {"disciple": self.profile2.id}
        form = GroupMemberDiscipleForm(
            data=form_data,
            profile=self.profile1,
        )

        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        """
        Test that the form is invalid with incorrect data.
        """
        form_data = {
            "disciple": 999,
        }
        form = GroupMemberDiscipleForm(
            data=form_data,
            profile=self.profile1,
        )

        self.assertFalse(form.is_valid())


class TestDiscipleshipFilterForm(TestCase):
    def test_filter_form_initialization(self):
        """
        Test that the form initializes with the correct choices.
        """
        form = DiscipleshipFilterForm()

        # Check the initial choices for filter_group
        self.assertEqual(
            form.fields["filter_group"].choices,
            [
                ("", "----------"),
                ("group_member", "Group member"),
                ("first_12", "First 12"),
                ("first_3", "First 3"),
                ("sent_forth", "Sent forth"),
            ],
        )

        # Check the initial choices for filter_status
        self.assertEqual(
            form.fields["filter_status"].choices,
            [
                ("", "----------"),
                ("all", "All"),
                ("ongoing", "Ongoing"),
                ("completed", "Completed"),
            ],
        )

    def test_filter_form_valid_data(self):
        """
        Test that the form is valid with correct data.
        """
        form_data = {
            "filter_group": "first_3",
            "filter_status": "ongoing",
        }
        form = DiscipleshipFilterForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_filter_form_invalid_data(self):
        """
        Test that the form is invalid with incorrect data.
        """
        form_data = {
            "filter_group": "invalid_choice",
            "filter_status": "invalid_choice",
        }
        form = DiscipleshipFilterForm(data=form_data)

        self.assertFalse(form.is_valid())

    def test_filter_form_empty_data(self):
        """
        Test that the form is valid when no data is submitted.
        """
        form_data = {}
        form = DiscipleshipFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["filter_group"], "")
        self.assertEqual(form.cleaned_data["filter_status"], "")
