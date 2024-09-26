"""
Models for the `actionapprovals` app.
"""

from datetime import timedelta

from django.db import models, transaction
from django.utils import timezone

from kns.core.modelmixins import TimestampedModel
from kns.core.models import Setting
from kns.groups.models import Group, GroupMember
from kns.profiles.models import Profile


class ActionApproval(TimestampedModel, models.Model):
    """
    Represents a base model for any action that requires approval from a leader.

    Attributes
    ----------
    created_by : ForeignKey (Profile)
        The profile of the user who initiated the approval request.
    consumer_group : ForeignKey (Group)
        The group for which the approval action is requested.
    status : CharField
        The current status of the approval request, defaulting to "pending".
    approved_by : ForeignKey (Profile)
        The profile of the user who approved the action.
    read : BooleanField
        Indicates whether the approval request has been read.
    timeout_duration : DurationField
        The duration before the request expires, defaults to 7 days.
    approved_at : DateTimeField
        The timestamp when the request was approved.
    """

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_EXPIRED = "expired"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_EXPIRED, "Expired"),
    ]

    created_by = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="initiated_approvals",
    )

    consumer_group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="approval_requests",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
    )

    approved_by = models.ForeignKey(
        Profile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_actions",
    )

    read = models.BooleanField(default=False)

    timeout_duration = models.DurationField(default=timedelta(days=7))

    approved_at = models.DateTimeField(null=True, blank=True)

    def check_timeout(self):
        """
        Check if the approval request has timed out based on the
        `timeout_duration`.
        """
        if (
            self.status == self.STATUS_PENDING
            and (self.created_at + self.timeout_duration) < timezone.now()
        ):
            self.status = self.STATUS_EXPIRED
            self.save()

    def can_approve_or_reject(self, consumer: Profile) -> bool:
        """
        Determine if the specified `consumer` can approve or reject the request.

        Parameters
        ----------
        consumer : Profile
            The profile of the user attempting to approve or reject the request.

        Returns
        -------
        bool
            True if the consumer is the leader of the consumer group, otherwise False.
        """
        return self.consumer_group.leader == consumer

    def approve(self, consumer: Profile) -> None:
        """
        Approve the action if it is still in the 'pending' status and
        the `consumer` is allowed to approve it.

        Parameters
        ----------
        consumer : Profile
            The profile of the user approving the action.
        """
        if self.status == self.STATUS_PENDING and self.can_approve_or_reject(consumer):
            self.approved_by = consumer
            self.status = self.STATUS_APPROVED
            self.approved_at = timezone.now()
            self.save()

    def __str__(self) -> str:
        """
        String representation of the ActionApproval instance.

        Returns
        -------
        str
            A string representation of the approval request.
        """
        return f"Approval request by {self.created_by}"


class PromoteToLeaderRole(models.Model):  # pragma: no cover
    """
    Represents the action of promoting a member to leader.

    Attributes
    ----------
    new_leader : ForeignKey (Profile)
        The profile being promoted to a leader role.
    approval : OneToOneField (ActionApproval)
        The associated approval request for this promotion action.
    """

    new_leader = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="leader_promotions",
    )
    approval = models.OneToOneField(
        ActionApproval,
        on_delete=models.CASCADE,
        related_name="promote_to_leader_action",
    )

    def perform_action(self) -> None:
        """
        Execute the action of promoting the `new_leader` to a leader role.

        Raises
        ------
        ValueError
            If promotion fails.
        -------
        None
        """
        try:
            self.new_leader.make_leader()
        except Exception as e:
            raise ValueError(f"Failed to promote {self.new_leader}: {e}")

    def __str__(self) -> str:
        """
        String representation of the PromoteToLeaderRole instance.

        Returns
        -------
        str
            A string representation of the promotion action.
        """
        return f"Promote {self.new_leader.get_full_name()} to a leader role"

    @staticmethod
    def requires_action_approval(created_by: Profile, new_leader: Profile) -> bool:
        """
        Determine whether promoting the `new_leader` to a leader role requires action approval.

        Parameters
        ----------
        created_by : Profile
            The profile initiating the action.
        new_leader : Profile
            The profile being promoted to a leader role.

        Returns
        -------
        bool
            True if approval is required, otherwise False.
        """

        # Retrieve the setting that determines if role change approval is required
        setting = Setting.get_or_create_setting()

        # If the change_role_approval_required setting is False, no approval is needed
        if not setting.change_role_approval_required:
            return False

        # Check if the created_by profile is part of a group
        try:
            group_member = GroupMember.objects.get(profile=created_by)
        except GroupMember.DoesNotExist:
            # If the profile is not part of any group, no approval is required
            return False

        # Check if the group is an origin group (e.g., if the parent is None)
        if group_member.group.parent is None:
            return False

        # If the profile is part of a group and it is not the origin group, approval is required
        return True

    @transaction.atomic
    def create_action_approval(
        self, new_leader: Profile, created_by: Profile
    ) -> "PromoteToLeaderRole":
        """
        Create an ActionApproval for promoting a member to leader.

        Parameters
        ----------
        new_leader : Profile
            The profile being promoted to a leader role.
        created_by : Profile
            The profile initiating the action.

        Returns
        -------
        PromoteToLeaderRole
            The created PromoteToLeaderRole instance.
        """
        if not new_leader.group_member.exists():
            raise ValueError(
                "The user must be part of a group to be promoted to leader."
            )

        group = Group.objects.filter(members=new_leader).first()

        approval = ActionApproval.objects.create(
            created_by=created_by,
            consumer_group=group,
            status=ActionApproval.STATUS_PENDING,
        )

        promote_action = PromoteToLeaderRole.objects.create(
            new_leader=new_leader,
            approval=approval,
        )

        return promote_action
