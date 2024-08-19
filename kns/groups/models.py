"""
Models for the `groups` app.
"""

from collections import Counter
from uuid import uuid4

from cloudinary.models import CloudinaryField
from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

from kns.core.modelmixins import ModelWithLocation, TimestampedModel
from kns.profiles.models import Profile


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

    description = models.TextField()

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
        Return the absolute URL to access a detail view of this group.

        Returns
        -------
        str
            The absolute URL of the group's detail view.
        """
        return reverse(
            "groups:group_detail",
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
        external_persons_count = 0
        for group_member in self.group_members():
            if group_member.role == "external_person":
                external_persons_count += 1
        return external_persons_count

    def male_count(self):
        """
        Return the count of male members in the group.

        Returns
        -------
        int:
            The total number of male members.
        """
        male_count = 0
        for group_member in self.group_members():
            if group_member.gender == "male":
                male_count += 1
        return male_count

    def female_count(self):
        """
        Return the count of female members in the group.

        Returns
        -------
        int:
            The total number of female members.
        """
        female_count = 0
        for group_member in self.group_members():
            if group_member.gender == "female":
                female_count += 1
        return female_count

    def mentors_count(self):
        """
        Return the count of members who are mentors in the group.

        Returns
        -------
        int:
            The total number of mentors in the group.
        """
        mentors_count = 0
        for group_member in self.group_members():
            if group_member.is_mentor:
                mentors_count += 1
        return mentors_count

    def skill_trainers_count(self):
        """
        Return the count of skill trainers in the group.

        Returns
        -------
        int:
            The total number of skill trainers in the group.
        """
        skill_trainers_count = 0
        for group_member in self.group_members():
            if group_member.is_skill_training_facilitator:
                skill_trainers_count += 1
        return skill_trainers_count

    def movement_trainers_count(self):
        """
        Return the count of movement trainers in the group.

        Returns
        -------
        int:
            The total number of movement trainers in the group.
        """
        movement_trainers_count = 0
        for group_member in self.group_members():
            if group_member.is_movement_training_facilitator:
                movement_trainers_count += 1
        return movement_trainers_count

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
