"""
Serializers for the `levels` app.
"""

from rest_framework import serializers

from .models import Level, LevelSublevel, Sublevel


class LevelSerializer(serializers.ModelSerializer):
    """
    Serializer for the Level model.

    This serializer includes basic information about a level, including its
    ID, title, content, and slug, as well as a list of sublevels associated
    with the level.

    Attributes
    ----------
    sublevels : SerializerMethodField
        A field that provides the sublevels related to this level via the
        `get_sublevels` method.
    """

    sublevels = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = [
            "id",
            "title",
            "content",
            "slug",
            "sublevels",
        ]

    def get_sublevels(self, obj):
        """
        Retrieve and serialize the sublevels associated with a given level.

        This method filters the LevelSublevel objects that link a level to its
        sublevels and serializes the sublevels using the SublevelSerializer.

        Parameters
        ----------
        obj : Level
            The Level instance for which sublevels are retrieved.

        Returns
        -------
        list
            A list of serialized sublevel data.
        """
        sublevel_objs = LevelSublevel.objects.filter(
            level=obj,
        ).select_related("sublevel")

        sublevels_data = [ls.sublevel for ls in sublevel_objs]

        return SublevelSerializer(
            sublevels_data,
            many=True,
        ).data


class SublevelSerializer(serializers.ModelSerializer):
    """
    Serializer for the Sublevel model.

    This serializer includes basic information about a sublevel, including its
    ID, title, content, and slug.

    Attributes
    ----------
    Meta : class
        Defines the model and fields to be included in the serialized data.
    """

    class Meta:
        model = Sublevel
        fields = [
            "id",
            "title",
            "content",
            "slug",
        ]
