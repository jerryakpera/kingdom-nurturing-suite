from django.test import TestCase

from kns.custom_user.models import User
from kns.groups.models import Group
from kns.groups.templatetags.groups_custom_tags import is_leader_of_parent_group
from kns.groups.tests import test_constants
from kns.profiles.models import Profile


class TestIsLeaderOfParentGroupFilterTests(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            email="testuser@example.com",
            password="password",
        )
        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="password",
        )
        self.user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="password",
        )

        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.profile3 = self.user3.profile

        self.profile3.delete()

        # Create a group
        self.origin_group = Group.objects.create(
            leader=self.profile1,
            name="Test Group",
            slug="test-group",
            description=test_constants.VALID_GROUP_DESCRIPTION,
        )

        self.child_group = Group.objects.create(
            name="Parent Group",
            slug="parent-group",
            description="A parent group",
            leader=self.profile2,
            parent=self.origin_group,
        )

    def test_user_without_profile(self):
        result = is_leader_of_parent_group(
            self.profile3,
            self.child_group,
        )

        self.assertFalse(
            result,
            "Should return False if the user does not have a profile.",
        )

    def test_group_without_parent(self):
        result = is_leader_of_parent_group(
            self.user2,
            self.origin_group,
        )

        self.assertFalse(
            result,
            "Should return False if the group does not have a parent group.",
        )

        result2 = is_leader_of_parent_group(
            self.user1,
            self.origin_group,
        )

        self.assertTrue(
            result2,
            "Should return True if the group does not have a parent group.",
        )

    def test_user_is_leader_of_parent_group(self):
        result = is_leader_of_parent_group(
            self.user1,
            self.child_group,
        )

        self.assertTrue(
            result,
            "Should return True if the user is the leader of the parent group.",
        )

    def test_user_is_not_leader_of_parent_group(self):
        result = is_leader_of_parent_group(
            self.user3,
            self.child_group,
        )

        self.assertFalse(
            result,
            "Should return False if the user is not the leader of the parent group.",
        )
