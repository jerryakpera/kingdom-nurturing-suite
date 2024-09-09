from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from kns.custom_user.models import User
from kns.groups.models import Group
from kns.groups.serializers import GroupSerializer


class TestGroupDescendantsAPI(APITestCase):
    def setUp(self):
        """
        Set up the test environment by creating users and groups.
        """
        self.client = APIClient()

        # Create users
        self.user1 = User.objects.create_user(
            email="testuser1@example.com",
            password="password123",
        )

        self.user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="password123",
        )

        self.user3 = User.objects.create_user(
            email="testuser3@example.com",
            password="password123",
        )

        # Create groups
        self.parent_group = Group.objects.create(
            leader=self.user1.profile,
            name="Parent Group",
            slug="parent-group",
            description="This is the parent group.",
        )

        self.child_group = Group.objects.create(
            leader=self.user2.profile,
            name="Child Group",
            slug="child-group",
            description="This is a child group.",
            parent=self.parent_group,
        )

        self.grandchild_group = Group.objects.create(
            leader=self.user3.profile,
            name="Grandchild Group",
            slug="grandchild-group",
            description="This is a grandchild group.",
            parent=self.child_group,
        )

    def test_group_descendants_valid_group(self):
        """
        Test retrieving a group and its descendants with a valid group ID.
        """
        url = reverse(
            "api:group_descendants",
            kwargs={
                "pk": self.parent_group.pk,
            },
        )

        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        # Verify that the response data matches the serialized group
        expected_data = GroupSerializer(self.parent_group).data

        self.assertEqual(
            response.data,
            expected_data,
        )

    def test_group_descendants_invalid_group(self):
        """
        Test retrieving a group that does not exist.
        """
        non_existent_pk = 9999  # Assuming this PK doesn't exist

        url = reverse(
            "api:group_descendants",
            kwargs={
                "pk": non_existent_pk,
            },
        )

        response = self.client.get(url)

        # Check if the response status code is 404 Not Found
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        # Verify that the error message is correct
        self.assertEqual(
            response.data["detail"],
            "Group not found.",
        )

    def test_group_descendants_no_descendants(self):
        """
        Test retrieving a group that has no descendants.
        """
        url = reverse(
            "api:group_descendants",
            kwargs={
                "pk": self.grandchild_group.pk,
            },
        )

        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        # Verify that the response data matches the serialized group
        expected_data = GroupSerializer(self.grandchild_group).data

        self.assertEqual(response.data, expected_data)

    def test_group_descendants_nested_structure(self):
        """
        Test the nested structure of the descendants in the serialized data.
        """
        url = reverse(
            "api:group_descendants",
            kwargs={
                "pk": self.parent_group.pk,
            },
        )

        response = self.client.get(url)

        # Check if the response contains the children correctly
        self.assertIn("children", response.data)

        self.assertEqual(
            len(response.data["children"]),
            1,
        )

        self.assertEqual(
            response.data["children"][0]["name"],
            "Child Group",
        )

        # Check the grandchild group in the nested structure
        child = response.data["children"][0]

        self.assertIn("children", child)
        self.assertEqual(
            len(child["children"]),
            1,
        )

        self.assertEqual(
            child["children"][0]["name"],
            "Grandchild Group",
        )

    def test_group_descendants_authentication(self):
        """
        Test that the endpoint works for authenticated users.
        """
        # Authenticate the client
        self.client.force_authenticate(user=self.user1)

        url = reverse(
            "api:group_descendants",
            kwargs={
                "pk": self.parent_group.pk,
            },
        )

        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_group_descendants_unauthenticated(self):
        """
        Test that the endpoint works for unauthenticated users if allowed.
        """
        # Log out the client to ensure unauthenticated request
        self.client.logout()

        url = reverse(
            "api:group_descendants",
            kwargs={
                "pk": self.parent_group.pk,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
