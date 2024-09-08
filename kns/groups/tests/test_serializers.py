from django.test import TestCase
from rest_framework.exceptions import ValidationError

from kns.custom_user.models import User
from kns.groups.models import Group
from kns.groups.serializers import GroupSerializer


class TestGroupSerializer(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating users and groups.
        """
        self.user1 = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )
        self.profile1 = self.user1.profile

        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="password123",
        )
        self.profile2 = self.user2.profile

        self.user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="password123",
        )
        self.profile3 = self.user3.profile

        # Create parent group
        self.parent_group = Group.objects.create(
            leader=self.profile1,
            name="Parent Group",
            slug="parent-group",
            description="This is the parent group.",
        )

        # Create child group
        self.child_group = Group.objects.create(
            leader=self.profile2,
            name="Child Group",
            slug="child-group",
            description="This is the child group.",
            parent=self.parent_group,
        )

        # Create grandchild group
        self.grandchild_group = Group.objects.create(
            leader=self.profile3,
            name="Grandchild Group",
            slug="grandchild-group",
            description="This is the grandchild group.",
            parent=self.child_group,
        )

    def test_serializer_fields(self):
        """
        Test that the serializer contains the expected fields.
        """
        serializer = GroupSerializer(self.parent_group)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("slug", data)
        self.assertIn("image", data)
        self.assertIn("children", data)
        self.assertIn("created_at", data)
        self.assertIn("leader_name", data)
        self.assertIn("description", data)
        self.assertIn("member_count", data)
        self.assertIn("location_display", data)

    def test_children_field(self):
        """
        Test that the children field returns the correct nested data.
        """
        serializer = GroupSerializer(self.parent_group)
        data = serializer.data

        # The parent group should have one child group
        self.assertEqual(len(data["children"]), 1)
        self.assertEqual(data["children"][0]["name"], "Child Group")

        # The child group should have one grandchild group
        child_serializer = GroupSerializer(self.child_group)

        child_data = child_serializer.data

        self.assertEqual(len(child_data["children"]), 1)
        self.assertEqual(
            child_data["children"][0]["name"],
            "Grandchild Group",
        )

    def test_member_count_field(self):
        """
        Test that the member_count field returns the correct number of members.
        """
        # At this point, no members are added to the groups, so member count should be 0
        serializer = GroupSerializer(self.parent_group)
        data = serializer.data

        self.assertEqual(data["member_count"], 0)

        # Add a member to the parent group
        self.parent_group.add_member(self.profile2)

        serializer = GroupSerializer(self.parent_group)
        data = serializer.data

        self.assertEqual(data["member_count"], 1)
