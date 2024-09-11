"""
Serializers for the `levels` app.
"""

from rest_framework import serializers

from .models import Classification, ClassificationSubclassification, Subclassification


class ClassificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Classification model.

    This serializer includes basic information about a classification, including its
    ID, title, content, slug, and order. It also provides a list of subclassifications
    associated with the classification via the `get_subclassifications` method.

    Attributes
    ----------
    subclassifications : SerializerMethodField
        A field that provides the subclassifications related to this classification
        via the `get_subclassifications` method.
    """

    subclassifications = serializers.SerializerMethodField()

    class Meta:
        model = Classification
        fields = [
            "id",
            "title",
            "content",
            "slug",
            "order",
            "subclassifications",
        ]

    def get_subclassifications(self, obj):
        """
        Retrieve and serialize the subclassifications associated with a
        given classification.

        This method filters the ClassificationSubclassification objects that
        link a classification to its subclassifications and serializes the
        subclassifications using the SubclassificationSerializer.

        Parameters
        ----------
        obj : Classification
            The Classification instance for which subclassifications are
            retrieved.

        Returns
        -------
        list
            A list of serialized subclassification data.
        """
        subclassification_objs = ClassificationSubclassification.objects.filter(
            classification=obj,
        ).select_related(
            "subclassification",
        )

        subclassifications_data = [
            ls.subclassification for ls in subclassification_objs
        ]

        return SubclassificationSerializer(
            subclassifications_data,
            many=True,
        ).data


class SubclassificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Subclassification model.

    This serializer includes basic information about a subclassification,
    including its ID, title, content, and slug.

    Attributes
    ----------
    Meta : class
        Defines the model and fields to be included in the serialized data.
    """

    class Meta:
        model = Subclassification
        fields = [
            "id",
            "title",
            "content",
            "slug",
        ]
