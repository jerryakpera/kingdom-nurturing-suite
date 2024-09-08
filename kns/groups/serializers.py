"""
This module contains the serializer for the Group model.
"""

from rest_framework import serializers

from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the Group model. This serializer handles nested group data,
    leader information, member count, and other group-related details.
    """

    children = serializers.SerializerMethodField()
    leader_name = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "slug",
            "image",
            "children",
            "created_at",
            "leader_name",
            "description",
            "member_count",
            "location_display",
        ]

    def get_children(self, obj):
        """
        Retrieve the child groups of the current group.

        Parameters
        ----------
        obj : Group
            The current Group instance.

        Returns
        -------
        list
            A list of serialized child groups.
        """
        serializer = GroupSerializer(obj.get_children(), many=True)
        return serializer.data

    def get_leader_name(self, obj):
        """
        Retrieve the name of the group's leader.

        Parameters
        ----------
        obj : Group
            The current Group instance.

        Returns
        -------
        str
            The name of the group's leader or "No leader assigned" if no leader exists.
        """
        return str(obj.leader) if obj.leader else "No leader assigned"

    def get_member_count(self, obj):
        """
        Retrieve the number of members in the group.

        Parameters
        ----------
        obj : Group
            The current Group instance.

        Returns
        -------
        int
            The number of members in the group.
        """
        return obj.members.count()
