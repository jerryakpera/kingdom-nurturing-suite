import pytest
from django.db import IntegrityError
from django.test import TestCase

from kns.custom_user.models import User
from kns.faith_milestones.models import (
    FaithMilestone,
    GroupFaithMilestone,
    ProfileFaithMilestone,
)
from kns.groups.models import Group


class TestFaithMilestoneModel(TestCase):
    def setUp(self):
        """
        Setup method to create a Profile instance linked to the test user.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )

        self.profile = self.user.profile

        self.profile.first_name = "Test"
        self.profile.last_name = "User"

        self.profile.save()

    def test_faith_milestone_creation(self):
        """
        Test that a FaithMilestone instance can be created and is properly saved.
        """
        milestone = FaithMilestone.objects.create(
            title="Baptism",
            description="Successfully baptized.",
            type="profile",
            author=self.profile,
        )

        self.assertEqual(milestone.title, "Baptism")
        self.assertEqual(
            milestone.description,
            "Successfully baptized.",
        )
        self.assertEqual(milestone.type, "profile")
        self.assertEqual(milestone.author, self.profile)

    def test_faith_milestone_str_method(self):
        """
        Test that the __str__ method returns the title of the faith milestone.
        """
        milestone = FaithMilestone.objects.create(
            title="Baptism",
            description="Successfully baptized.",
            type="profile",
            author=self.profile,
        )

        self.assertEqual(str(milestone), "Baptism")


class TestProfileFaithMilestoneModel(TestCase):
    def setUp(self):
        """
        Setup method to create Profile and FaithMilestone instances.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )
        self.profile = self.user.profile
        self.profile.first_name = "John"
        self.profile.last_name = "Doe"
        self.profile.save()

        self.milestone = FaithMilestone.objects.create(
            title="Baptism",
            description="Successfully baptized.",
            type="profile",
            author=self.profile,
        )

    def test_profile_faith_milestone_creation(self):
        """
        Test that a ProfileFaithMilestone instance can be created and is properly saved.
        """
        profile_milestone = ProfileFaithMilestone.objects.create(
            profile=self.profile,
            faith_milestone=self.milestone,
        )

        self.assertEqual(
            profile_milestone.profile,
            self.profile,
        )
        self.assertEqual(
            profile_milestone.faith_milestone,
            self.milestone,
        )

    def test_profile_faith_milestone_unique_together(self):
        """
        Test that the combination of profile and faith milestone
        is unique in ProfileFaithMilestone.
        """
        ProfileFaithMilestone.objects.create(
            profile=self.profile,
            faith_milestone=self.milestone,
        )

        with pytest.raises(IntegrityError) as excinfo:
            ProfileFaithMilestone.objects.create(
                profile=self.profile,
                faith_milestone=self.milestone,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_profile_faith_milestone_str_method(self):
        """
        Test that the __str__ method returns the correct string representation.
        """
        profile_milestone = ProfileFaithMilestone.objects.create(
            profile=self.profile,
            faith_milestone=self.milestone,
        )

        self.assertEqual(
            str(profile_milestone),
            f"{self.profile.get_full_name()} - {self.milestone.title}",
        )


class TestGroupFaithMilestoneModel(TestCase):
    def setUp(self):
        """
        Setup method to create Group and FaithMilestone instances.
        """
        self.user = User.objects.create_user(
            email="john.doe@example.com",
            password="password",
        )
        self.profile = self.user.profile
        self.group = Group.objects.create(
            name="Youth Group",
            leader=self.profile,
        )
        self.milestone = FaithMilestone.objects.create(
            title="Mission Trip",
            description="Participated in a mission trip.",
            type="group",
            author=self.profile,
        )

    def test_group_faith_milestone_creation(self):
        """
        Test that a GroupFaithMilestone instance can be created and
        is properly saved.
        """
        group_milestone = GroupFaithMilestone.objects.create(
            group=self.group,
            faith_milestone=self.milestone,
        )

        self.assertEqual(group_milestone.group, self.group)
        self.assertEqual(
            group_milestone.faith_milestone,
            self.milestone,
        )

    def test_group_faith_milestone_unique_together(self):
        """
        Test that the combination of group and faith milestone is unique in GroupFaithMilestone.
        """
        GroupFaithMilestone.objects.create(
            group=self.group,
            faith_milestone=self.milestone,
        )

        with pytest.raises(IntegrityError) as excinfo:
            GroupFaithMilestone.objects.create(
                group=self.group,
                faith_milestone=self.milestone,
            )

        assert "UNIQUE constraint failed" in str(excinfo.value)

    def test_group_faith_milestone_str_method(self):
        """
        Test that the __str__ method returns the correct string representation.
        """
        group_milestone = GroupFaithMilestone.objects.create(
            group=self.group,
            faith_milestone=self.milestone,
        )

        self.assertEqual(
            str(group_milestone),
            f"{self.group} - {self.milestone.title}",
        )
