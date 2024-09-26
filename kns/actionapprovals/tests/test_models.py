from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from kns.actionapprovals.models import ActionApproval, PromoteToLeaderRole
from kns.custom_user.models import User
from kns.groups.models import Group


class TestActionApprovalModel(TestCase):
    def setUp(self):
        # Create a user and their profile
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
        )
        self.profile = self.user.profile

        # Create a group and assign the profile as leader
        self.group = Group.objects.create(
            leader=self.profile,
            name="Test Group",
            slug="test-group",
            location_country="NG",
            location_city="Bauchi",
            description="A group for testing.",
        )

        # Create an ActionApproval instance
        self.approval = ActionApproval.objects.create(
            created_by=self.profile,
            consumer_group=self.group,
            status=ActionApproval.STATUS_PENDING,
            read=False,
        )

    def test_approve_action(self):
        """Test the approve method of ActionApproval."""
        # Create another user to approve the action
        user2 = User.objects.create_user(
            email="testuser2@example.com",
            password="password123",
        )
        profile2 = user2.profile
        self.group.leader = profile2
        self.group.save()

        # Approve the action
        self.approval.approve(profile2)

        # Verify the action is approved
        self.assertEqual(self.approval.status, ActionApproval.STATUS_APPROVED)
        self.assertEqual(self.approval.approved_by, profile2)
        self.assertIsNotNone(self.approval.approved_at)

    def test_check_timeout(self):
        """Test the check_timeout method."""
        # Set created_at to a time in the past that exceeds the timeout duration
        self.approval.created_at = timezone.now() - timedelta(days=8)
        self.approval.check_timeout()

        # Verify that the status is updated to expired
        self.assertEqual(self.approval.status, ActionApproval.STATUS_EXPIRED)

    def test_can_approve_or_reject(self):
        """Test the can_approve_or_reject method."""
        # Test if a non-leader profile cannot approve
        non_leader_user = User.objects.create_user(
            email="nonleader@example.com",
            password="password123",
        )
        non_leader_profile = non_leader_user.profile

        self.assertFalse(self.approval.can_approve_or_reject(non_leader_profile))

        # Test if a leader can approve
        self.assertTrue(self.approval.can_approve_or_reject(self.profile))

    def test_str_representation(self):
        """Test the string representation of ActionApproval."""
        self.assertEqual(str(self.approval), f"Approval request by {self.profile}")
