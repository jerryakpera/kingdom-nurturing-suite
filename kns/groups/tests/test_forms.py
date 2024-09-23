"""
Tests for the forms in the `groups` app.
"""

from django.test import TestCase

from kns.custom_user.models import User
from kns.faith_milestones.models import FaithMilestone, GroupFaithMilestone
from kns.groups.models import Group
from kns.mentorships.models import MentorshipArea
from kns.skills.models import Skill
from kns.vocations.models import Vocation

from ..forms import (
    GroupBasicFilterForm,
    GroupDemographicsFilterForm,
    GroupFaithMilestoneFilterForm,
    GroupForm,
    GroupMembersFilterForm,
    GroupMentorshipAreasFilterForm,
    GroupSkillsInterestsFilterForm,
    GroupVocationsFilterForm,
)
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

    def test_group_invalid_country_code(self):
        self.form_data["location_country"] = "ZZ"

        form = GroupBasicFilterForm(data=self.form_data)

        # Assert that the form is invalid
        self.assertFalse(form.is_valid())
        self.assertIn("location_country", form.errors)

        self.assertEqual(
            form.errors["location_country"],
            [
                "Select a valid choice. ZZ is not one of the available choices.",
            ],
        )

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


class TestGroupMembersFilterForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        self.form_data = {
            "num_members": 10,
            "num_leaders": 2,
            "num_skill_trainers": 3,
            "num_movement_trainers": 1,
            "num_mentors": 4,
            "num_external_persons": 5,
        }

    def test_group_members_filter_form_valid(self):
        form = GroupMembersFilterForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_group_members_filter_form_invalid(self):
        # Test with a negative number for members
        self.form_data["num_members"] = -1
        form = GroupMembersFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "num_members", form.errors
        )  # Ensure the error is set for num_members

    def test_group_leaders_filter_form_invalid(self):
        # Test with a negative number for leaders
        self.form_data["num_leaders"] = -1
        form = GroupMembersFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("num_leaders", form.errors)

    def test_group_skill_trainers_filter_form_invalid(self):
        # Test with a negative number for skill trainers
        self.form_data["num_skill_trainers"] = -1
        form = GroupMembersFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("num_skill_trainers", form.errors)

    def test_group_movement_trainers_filter_form_invalid(self):
        # Test with a negative number for movement trainers
        self.form_data["num_movement_trainers"] = -1
        form = GroupMembersFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("num_movement_trainers", form.errors)

    def test_group_mentors_filter_form_invalid(self):
        # Test with a negative number for mentors
        self.form_data["num_mentors"] = -1
        form = GroupMembersFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("num_mentors", form.errors)

    def test_group_external_persons_filter_form_invalid(self):
        # Test with a negative number for external persons
        self.form_data["num_external_persons"] = -1
        form = GroupMembersFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("num_external_persons", form.errors)

    def test_group_members_filter_form_zero(self):
        # Test with zero members
        self.form_data["num_members"] = 0
        form = GroupMembersFilterForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["num_members"], 0)

    def test_empty_form(self):
        form = GroupMembersFilterForm(data={})
        self.assertTrue(form.is_valid())  # All fields are optional

    def test_partial_form(self):
        # Test a form with only some fields filled
        partial_data = {
            "num_members": 5,
        }
        form = GroupMembersFilterForm(data=partial_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["num_members"], 5)
        self.assertIsNone(
            form.cleaned_data.get("num_leaders")
        )  # Should be None since it's not provided

    def test_non_integer_input(self):
        # Test with a non-integer input for number of members
        self.form_data["num_members"] = "ten"
        form = GroupMembersFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("num_members", form.errors)

    def test_exceeding_large_number(self):
        # Test with an extremely large number
        self.form_data["num_members"] = 1000000
        form = GroupMembersFilterForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["num_members"], 1000000)


class TestGroupDemographicsFilterForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        self.form_data = {
            "num_male_members": 10,
            "num_female_members": 5,
            "more_male_members": False,
            "more_female_members": False,
        }

    def test_group_demographics_filter_form_valid(self):
        form = GroupDemographicsFilterForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_group_demographics_filter_form_invalid_male(self):
        # Test with a negative number for male members
        self.form_data["num_male_members"] = -1
        form = GroupDemographicsFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("num_male_members", form.errors)

    def test_group_demographics_filter_form_invalid_female(self):
        # Test with a negative number for female members
        self.form_data["num_female_members"] = -1
        form = GroupDemographicsFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("num_female_members", form.errors)

    def test_group_demographics_filter_form_zero_male(self):
        # Test with zero male members
        self.form_data["num_male_members"] = 0
        form = GroupDemographicsFilterForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["num_male_members"], 0)

    def test_group_demographics_filter_form_zero_female(self):
        # Test with zero female members
        self.form_data["num_female_members"] = 0
        form = GroupDemographicsFilterForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["num_female_members"], 0)

    def test_empty_form(self):
        form = GroupDemographicsFilterForm(data={})
        self.assertTrue(form.is_valid())  # All fields are optional

    def test_partial_form(self):
        # Test a form with only some fields filled
        partial_data = {
            "num_male_members": 5,
        }
        form = GroupDemographicsFilterForm(data=partial_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["num_male_members"], 5)
        self.assertIsNone(form.cleaned_data.get("num_female_members"))  # Should be None

    def test_non_integer_input_male(self):
        # Test with a non-integer input for number of male members
        self.form_data["num_male_members"] = "ten"
        form = GroupDemographicsFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("num_male_members", form.errors)

    def test_non_integer_input_female(self):
        # Test with a non-integer input for number of female members
        self.form_data["num_female_members"] = "ten"
        form = GroupDemographicsFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("num_female_members", form.errors)

    def test_exceeding_large_number_male(self):
        # Test with an extremely large number for male members
        self.form_data["num_male_members"] = 1000000
        form = GroupDemographicsFilterForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["num_male_members"], 1000000)

    def test_exceeding_large_number_female(self):
        # Test with an extremely large number for female members
        self.form_data["num_female_members"] = 1000000
        form = GroupDemographicsFilterForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["num_female_members"], 1000000)


class TestGroupSkillsInterestsFilterForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        # Create mock data for skills and vocations
        self.skill1 = Skill.objects.create(
            title="Python",
            content="Content for a skill",
            author=self.user.profile,
        )
        self.skill2 = Skill.objects.create(
            title="Django",
            content="Content for a skill",
            author=self.user.profile,
        )

        self.vocation1 = Vocation.objects.create(
            title="Developer",
            description="Writes code",
            author=self.user.profile,
        )

        self.form_data = {
            "skills": [self.skill1.id, self.skill2.id],
            "unique_skills_count": 2,
            "num_skill_training_facilitators": 1,
            "num_movement_training_facilitators": 0,
            "interests": [self.skill1.id],
            "unique_interests_count": 2,
        }

    def test_group_skills_interests_filter_form_valid(self):
        form = GroupSkillsInterestsFilterForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_empty_form(self):
        form = GroupSkillsInterestsFilterForm(data={})
        self.assertTrue(form.is_valid())

    def test_partial_form(self):
        partial_data = {
            "skills": [self.skill1.id],
        }
        form = GroupSkillsInterestsFilterForm(data=partial_data)
        self.assertTrue(form.is_valid())

        # Compare the cleaned data to a list of skills
        self.assertEqual(
            list(form.cleaned_data["skills"]),
            [self.skill1],
        )
        self.assertIsNone(form.cleaned_data.get("unique_skills_count"))

    def test_invalid_unique_skills_count_negative(self):
        self.form_data["unique_skills_count"] = -1
        form = GroupSkillsInterestsFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("unique_skills_count", form.errors)

    def test_invalid_unique_interests_count_negative(self):
        self.form_data["unique_interests_count"] = -1
        form = GroupSkillsInterestsFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("unique_interests_count", form.errors)

    def test_non_integer_input_unique_interests_count(self):
        self.form_data["unique_interests_count"] = "two"
        form = GroupSkillsInterestsFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("unique_interests_count", form.errors)

    def test_valid_large_number_unique_skills_count(self):
        self.form_data["unique_skills_count"] = 25

        form = GroupSkillsInterestsFilterForm(
            data=self.form_data,
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["unique_skills_count"],
            25,
        )

    def test_exceeding_large_number_unique_skills_count(self):
        self.form_data["unique_skills_count"] = 1000000

        form = GroupSkillsInterestsFilterForm(
            data=self.form_data,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("unique_skills_count", form.errors)

    def test_valid_large_number_unique_interests_count(self):
        self.form_data["unique_interests_count"] = 25

        form = GroupSkillsInterestsFilterForm(
            data=self.form_data,
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["unique_interests_count"],
            25,
        )

    def test_exceeding_large_number_unique_interests_count(self):
        self.form_data["unique_interests_count"] = 1000000

        form = GroupSkillsInterestsFilterForm(data=self.form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("unique_interests_count", form.errors)


class TestGroupVocationsFilterForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.vocation1 = Vocation.objects.create(
            title="Developer",
            description="Writes code",
            author=self.user.profile,
        )

        self.form_data = {
            "vocations": [self.vocation1.id],
            "unique_vocations_count": 2,
        }

    def test_group_vocations_filter_form_valid(self):
        form = GroupVocationsFilterForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_empty_form(self):
        form = GroupVocationsFilterForm(data={})
        self.assertTrue(form.is_valid())

    def test_partial_form(self):
        partial_data = {
            "vocations": [self.vocation1.id],
        }
        form = GroupVocationsFilterForm(data=partial_data)
        self.assertTrue(form.is_valid())

        # Compare the cleaned data to a list of vocations
        self.assertEqual(
            list(form.cleaned_data["vocations"]),
            [self.vocation1],
        )
        self.assertIsNone(form.cleaned_data.get("unique_vocations_count"))

    def test_invalid_unique_vocations_count_negative(self):
        self.form_data["unique_vocations_count"] = -1
        form = GroupVocationsFilterForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("unique_vocations_count", form.errors)

    def test_exceeding_large_number_unique_vocations_count(self):
        self.form_data["unique_vocations_count"] = 10000

        form = GroupVocationsFilterForm(
            data=self.form_data,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("unique_vocations_count", form.errors)


class TestGroupMentorshipAreasFilterForm(TestCase):
    def setUp(self):
        """
        Set up valid form data for all tests.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.mentorship_area1 = MentorshipArea.objects.create(
            title="Developer",
            content="Writes code",
            author=self.user.profile,
        )

        self.form_data = {
            "mentorship_areas": [self.mentorship_area1.id],
            "unique_mentorship_areas_count": 2,
        }

    def test_group_mentorship_areas_filter_form_valid(self):
        form = GroupMentorshipAreasFilterForm(data=self.form_data)

        self.assertTrue(form.is_valid())

    def test_empty_form(self):
        form = GroupMentorshipAreasFilterForm(data={})
        self.assertTrue(form.is_valid())

    def test_partial_form(self):
        partial_data = {
            "mentorship_areas": [self.mentorship_area1.id],
        }
        form = GroupMentorshipAreasFilterForm(
            data=partial_data,
        )
        self.assertTrue(form.is_valid())

        # Compare the cleaned data to a list of mentorship areas
        self.assertEqual(
            list(
                form.cleaned_data["mentorship_areas"],
            ),
            [self.mentorship_area1],
        )
        self.assertIsNone(
            form.cleaned_data.get("unique_mentorship_areas_count"),
        )

    def test_invalid_unique_mentorship_areas_count_negative(self):
        self.form_data["unique_mentorship_areas_count"] = -1

        form = GroupMentorshipAreasFilterForm(
            data=self.form_data,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("unique_mentorship_areas_count", form.errors)

    def test_exceeding_large_number_unique_mentorship_areas_count(self):
        self.form_data["unique_mentorship_areas_count"] = 10000

        form = GroupMentorshipAreasFilterForm(
            data=self.form_data,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("unique_mentorship_areas_count", form.errors)


class TestGroupFaithMilestoneFilterForm(TestCase):
    def setUp(self):
        """
        Set up test data for filtering by faith milestones.
        """
        # Create users and assign faith milestones to groups
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

        # Create groups
        self.group1 = Group.objects.create(
            leader=self.profile1,
            name="Alpha Group",
            location_country="GH",
            location_city="Accra",
            description="Group for alpha members.",
        )

        self.group2 = Group.objects.create(
            leader=self.profile2,
            name="Beta Group",
            parent=self.group1,
            location_country="Nigeria",
            location_city="Kaduna",
            description="Group for beta members.",
        )

        # Create sample Faith Milestones
        self.faith_milestone1 = FaithMilestone.objects.create(
            author=self.profile1,
            title="Milestone 1",
            type="group",
            description="First faith milestone",
        )
        self.faith_milestone2 = FaithMilestone.objects.create(
            author=self.profile1,
            title="Milestone 2",
            type="group",
            description="Second faith milestone",
        )
        self.faith_milestone3 = FaithMilestone.objects.create(
            author=self.profile1,
            title="Unrelated Milestone",
            type="group",
            description="Milestone not related to profile",
        )

        # Assign faith milestones to profiles
        GroupFaithMilestone.objects.create(
            faith_milestone=self.faith_milestone1,
            group=self.group1,
        )

        GroupFaithMilestone.objects.create(
            faith_milestone=self.faith_milestone2,
            group=self.group1,
        )

    def test_form_initialization(self):
        """
        Test that the form initializes correctly with no errors.
        """
        form = GroupFaithMilestoneFilterForm()

        self.assertIsInstance(form, GroupFaithMilestoneFilterForm)

    def test_form_valid_faith_milestones_filter(self):
        """
        Test that filtering by faith milestones returns the correct profiles.
        """
        form_data = {"faith_milestones": [self.faith_milestone1.id]}
        form = GroupFaithMilestoneFilterForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertIn(
            self.faith_milestone1,
            form.cleaned_data["faith_milestones"],
        )

    def test_form_empty_filter(self):
        """
        Test that an empty form does not raise validation errors.
        """
        form = GroupFaithMilestoneFilterForm(data={})

        self.assertTrue(form.is_valid())
