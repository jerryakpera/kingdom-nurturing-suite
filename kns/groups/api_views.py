"""
This module contains API views for managing and retrieving group-related
data.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Group
from .serializers import GroupSerializer


@api_view(["GET"])
def group_descendants(request, pk):
    """
    Retrieve a group and its descendants based on the provided group ID (pk).

    Parameters
    ----------
    request : HttpRequest
        The request object that provides metadata about the request.
    pk : int
        The primary key (ID) of the group to retrieve.

    Returns
    -------
    Response
        A JSON response containing the serialized group data if found,
        or an error message with a 404 status if the group does not exist.
    """
    try:
        group = Group.objects.get(pk=pk)
    except Group.DoesNotExist:
        return Response(
            {
                "detail": "Group not found.",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # Serialize the group and its descendants
    serializer = GroupSerializer(group)
    return Response(serializer.data)
