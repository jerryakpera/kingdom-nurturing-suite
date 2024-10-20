"""
Models for the `groups` app.
"""

from collections import Counter
from datetime import date
from uuid import uuid4

from cloudinary.models import CloudinaryField
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

from kns.core.modelmixins import ModelWithLocation, TimestampedModel
from kns.onboarding.models import ProfileCompletionTask
from kns.profiles.models import Profile

from . import constants


class Group(TimestampedModel, ModelWithLocation, MPTTModel):
    """
    Model representing a group within the application.

    Attributes:
        name (str): The name of the group.
        slug (UUID): A unique identifier for the group.
        description (str): A text description of the group.
        leader (Profile): The profile of the group's leader.
        parent (Group): A reference to a parent group.
        image (CloudinaryField): An optional group image.
    """

    class MPTTMeta:
        """
        Meta options for MPTT (Modified Preorder Tree Traversal).
        """

        order_insertion_by = ["name"]

    class Meta:
        """
        Meta options for the Group model.
        """

        verbose_name = "Group"
        verbose_name_plural = "Groups"
        ordering = ["-created_at"]

    name = models.CharField(max_length=50)

    slug = models.SlugField(
        unique=True,
        default=uuid4,
        null=True,
        blank=True,
        editable=False,
    )

    description = models.TextField(
        validators=[
            MinLengthValidator(constants.GROUP_DESCRIPTION_MIN_LENGTH),
            MaxLengthValidator(constants.GROUP_DESCRIPTION_MAX_LENGTH),
        ]
    )

    leader = models.OneToOneField(
        Profile,
        related_name="group_led",
        on_delete=models.PROTECT,
    )

    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
    )

    image = CloudinaryField(
        null=True,
        blank=True,
        folder="kns/images/groups/",
    )

    def __str__(self) -> str:
        """
        Return the string representation of the group.

        Returns
        -------
        str
            The string representation of the group, including its name
            and location if available.
        """
        return_str = f"{self.name} - {self.location_country}"
        if self.location_city:
            return_str += f" ({self.location_city})"

        return return_str

    def get_absolute_url(self):
        """
        Return the absolute URL to access a overview view of this group.

        Returns
        -------
        str
            The absolute URL of the group's overview view.
        """
        return reverse(
            "groups:group_overview",
            kwargs={
                "group_slug": self.slug,
            },
        )

    def get_members_url(self):
        """
        Return the members URL to access the members view of this group.

        Returns
        -------
        str
            The members URL of the group.
        """
        return reverse(
            "groups:group_members",
            kwargs={
                "group_slug": self.slug,
            },
        )

    def get_activities_url(self):
        """
        Return the activities URL to access the activities view of this group.

        Returns
        -------
        str
            The activities URL of the group.
        """
        return reverse(
            "groups:group_activities",
            kwargs={
                "group_slug": self.slug,
            },
        )

    def get_subgroups_url(self):
        """
        Return the subgroups URL to access the subgroups view of this group.

        Returns
        -------
        str
            The subgroups URL of the group.
        """
        return reverse(
            "groups:group_subgroups",
            kwargs={
                "group_slug": self.slug,
            },
        )

    def location_display(self):
        """
        Return a string representation of the group's location.

        Returns
        -------
        str
            The location of the group formatted as "Country, City" or
            "Country" if no city is provided, or "None" if no location
            is provided.
        """
        location_str = "None"
        if self.location_country:
            location_str = self.location_country.name

            if self.location_city:
                location_str += f", {self.location_city}"

        return location_str

    def group_members(self):
        """
        Return a list of profiles of all the members in the group.

        Returns
        -------
        list[Profile]:
            A list of Profile instances representing the members
            of the group.
        """
        return [gm.profile for gm in self.members.all()]

    def add_member(self, profile):
        """
        Add a profile to the group if they are not already a member.

        Parameters
        ----------
        profile : Profile
            The profile to add to the group.

        Returns
        -------
        Profile
            The profile that was added (or already existed).
        """
        if not self.members.filter(profile=profile).exists():
            GroupMember.objects.create(
                profile=profile,
                group=self,
            )
        return profile

    def remove_member(self, profile):
        """
        Remove a profile from the group if they are a member.

        Parameters
        ----------
        profile : Profile
            The profile to remove from the group.

        Returns
        -------
        bool
            True if the profile was removed, False if they were not a member.
        """
        try:
            membership = GroupMember.objects.get(
                profile=profile,
                group=self,
            )
            membership.delete()

            return True
        except GroupMember.DoesNotExist:
            return False

    def leaders_count(self):
        """
        Return the count of leaders in the group.

        Returns
        -------
        int:
            The total number of leaders in the group.
        """
        return self.members.filter(profile__role="leader").count()

    def total_members_count(self):
        """
        Return the count of members in the group.

        Returns
        -------
        int:
            The total number of members in the group, including the
            leader.
        """
        return self.members.count() + 1

    def members_count(self):
        """
        Return the count of members with the role 'member'.

        Returns
        -------
        int:
            The total number of members with the role 'member'.
        """
        return self.members.filter(profile__role="member").count()

    def external_persons_count(self):
        """
        Return the count of members with the role 'external_person'.

        Returns
        -------
        int:
            The total number of members with the role 'external_person'.
        """
        return self.members.filter(
            profile__role="external_person",
        ).count()

    def male_count(self):
        """
        Return the count of male members in the group.

        Returns
        -------
        int:
            The total number of male members.
        """
        return self.members.filter(
            profile__gender="male",
        ).count()

    def female_count(self):
        """
        Return the count of female members in the group.

        Returns
        -------
        int:
            The total number of female members.
        """
        return self.members.filter(profile__gender="female").count()

    def mentors_count(self):
        """
        Return the count of members who are mentors in the group.

        Returns
        -------
        int:
            The total number of mentors in the group.
        """
        return self.members.filter(profile__is_mentor=True).count()

    def skill_trainers_count(self):
        """
        Return the count of skill trainers in the group.

        Returns
        -------
        int:
            The total number of skill trainers in the group.
        """
        return self.members.filter(
            profile__is_skill_training_facilitator=True,
        ).count()

    def movement_trainers_count(self):
        """
        Return the count of movement trainers in the group.

        Returns
        -------
        int:
            The total number of movement trainers in the group.
        """
        return self.members.filter(
            profile__is_movement_training_facilitator=True,
        ).count()

    def most_common_role(self):
        """
        Return the most common role among group members.

        Returns
        -------
        str or None:
            The most common role, or None if there are no roles.
        """
        roles = [member.role for member in self.group_members()]

        most_common = Counter(roles).most_common(1)[0][0]
        return most_common

    def is_member(self, profile):
        """
        Check if a given profile is a member of the group.

        Parameters
        ----------
        profile : Profile
            The profile to check.

        Returns
        -------
        bool
            True if the profile is a member of the group, False otherwise.
        """
        return self.members.filter(profile=profile).exists()

    def get_close_city_groups(self):
        """
        Return all groups within the same city as the groups location,
        that are descendants/siblings of the group.

        Returns
        -------
        QuerySet
            A queryset of groups that are descendants/siblings of this group and
            are in the same city or country as the group.
        """

        descendant_groups = None

        if self.parent:
            descendant_groups = self.parent.get_descendants()
        else:
            # Get all descendant groups of this group
            descendant_groups = self.get_descendants()

        # Filter based on city first, then country if city is not available
        close_groups = descendant_groups.filter(
            location_city=self.location_city,
        ).exclude(
            id=self.id,
        )

        return close_groups

    def get_close_country_groups(self):
        """
        Return all groups within the same country as the groups location,
        that are descendants/siblings of the group.

        Returns
        -------
        QuerySet
            A queryset of groups that are descendants/siblings of this group and
            are in the same country or country as the group.
        """

        descendant_groups = None

        if self.parent:
            descendant_groups = self.parent.get_descendants()
        else:
            # Get all descendant groups of this group
            descendant_groups = self.get_descendants()

        # Filter based on country first, then country if country is not available
        close_groups = descendant_groups.filter(
            location_country=self.location_country,
        ).exclude(
            id=self.id,
        )

        return close_groups

    def average_age(self):
        """
        Calculate the average age of all members in the group.

        Returns
        -------
        float or str:
            The average age of the group's members, rounded to one decimal place.
            Returns '---' if there are no members with a valid age.
        """
        members_with_age = [
            member.profile.get_age()
            for member in self.members.all()
            if member.profile.date_of_birth
        ]

        if members_with_age:
            return round(
                sum(members_with_age) / len(members_with_age),
                1,
            )

        return "---"

    def unique_skills(self):
        """
        Return a queryset of unique skills of all members in the group.

        Returns
        -------
        QuerySet:
            A queryset of unique skill titles of the group's members.
        """
        return (
            self.members.values_list("profile__skills__skill__title", flat=True)
            .distinct()
            .exclude(profile__skills__skill__title=None)
        )

    def unique_interests(self):
        """
        Return a queryset of unique interests of all members in the group.

        Returns
        -------
        QuerySet:
            A queryset of unique interest titles of the group's members.
        """
        return (
            self.members.values_list(
                "profile__interests__interest__title",
                flat=True,
            )
            .distinct()
            .exclude(
                profile__interests__interest__title=None,
            )
        )

    def sister_groups(self):
        """
        Return a queryset of the group's sister groups.

        Sister groups are groups that share the same parent group but are not the group itself.

        Returns
        -------
        QuerySet:
            A queryset of the group's sister groups (groups with the same parent).
        """
        return self.get_siblings(include_self=False)

    def child_groups(self):
        """
        Return a queryset of the group's child groups.

        Child groups are groups that are directly below the current group in the hierarchy.

        Returns
        -------
        QuerySet:
            A queryset of the group's child groups (direct descendants).
        """
        return self.get_children()


class GroupMember(TimestampedModel):
    """
    Model representing a member of a group.

    Attributes
    ----------
    profile (Profile):
        The profile of the group member.
    group (Group):
        The group to which the member belongs.
    role (str):
        The role of the group member (e.g., member, leader).
    """

    class Meta:
        """
        Meta options for the GroupMember model.
        """

        verbose_name = "Group Member"
        verbose_name_plural = "Group Members"
        unique_together = ("profile", "group")

        ordering = [
            "-created_at",
        ]

    profile = models.OneToOneField(
        Profile,
        related_name="group_in",
        on_delete=models.CASCADE,
    )

    group = models.ForeignKey(
        Group,
        related_name="members",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """
        Return the string representation of the group member,
        including their profile name and role.

        Returns
        -------
        str:
            The string representation of the group member, including
            their profile name and the group name.
        """
        return f"{self.profile.get_full_name()} ({self.group.name})"


@receiver(post_save, sender=Group)
def mark_register_group_complete(sender, instance, created, **kwargs):
    """
    Mark the 'register_group' task as complete when a group is created.

    Parameters
    ----------
    sender : type
        The model class that triggered the signal.
    instance : Group
        The instance of the group being saved.
    created : bool
        Whether the group was created or updated.
    **kwargs : dict
        Additional keyword arguments passed by the signal.
    """
    if created:
        # Assuming the leader of the group is the one who registered it
        profile = instance.leader

        register_group_task_exists = ProfileCompletionTask.objects.filter(
            profile=profile,
            task_name="register_group",
        ).exists()

        if register_group_task_exists:
            task = ProfileCompletionTask.objects.get(
                profile=profile,
                task_name="register_group",
            )

            if task:
                task.mark_complete()


@receiver(post_save, sender=GroupMember)
def mark_register_first_member_complete(sender, instance, created, **kwargs):
    """
    Mark the 'register_first_member' task as complete when the first member is added to the group.

    This signal is triggered after a GroupMember instance is saved. If it is the first
    member being added to the group, the leader of the group will have their
    'register_first_member' task marked as complete.

    Parameters
    ----------
    sender : type
        The model class that triggered the signal (GroupMember).
    instance : GroupMember
        The instance of the GroupMember model being saved.
    created : bool
        A boolean indicating if the GroupMember instance was newly created.
    **kwargs : dict
        Additional keyword arguments passed by the signal.
    """
    if created:
        # Check if it's the first member of the group
        group = instance.group

        if group.members.count() == 1:
            profile = group.leader

            task_exists = ProfileCompletionTask.objects.filter(
                profile=profile,
                task_name="register_first_member",
            ).exists()

            if task_exists:
                task = ProfileCompletionTask.objects.get(
                    profile=profile,
                    task_name="register_first_member",
                )

                if task:
                    task.mark_complete()
