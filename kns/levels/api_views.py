"""
Views for the level apis app.
"""

from django.http import JsonResponse

from .models import Level, Sublevel
from .serializers import LevelSerializer, SublevelSerializer


def levels_list(request):
    """
    Retrieve a list of all levels and return them as a JSON response.

    This view fetches all Level objects, serializes them using the
    LevelSerializer, and returns the serialized data as a JSON response.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.

    Returns
    -------
    JsonResponse
        A JSON response containing the list of serialized levels.
    """
    # Get all levels
    levels = Level.objects.all()

    # Serialize levels
    serializer = LevelSerializer(levels, many=True)

    # Return them as json response
    data = {
        "levels": serializer.data,
    }

    return JsonResponse(data, safe=False)


def level_detail(request, id):
    """
    Retrieve the details of a specific level by its ID and return them as a JSON response.

    This view fetches a Level object by its ID, serializes it using the
    LevelSerializer, and returns the serialized data as a JSON response.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    id : int
        The ID of the level to retrieve.

    Returns
    -------
    JsonResponse
        A JSON response containing the serialized level data.
    """
    level = Level.objects.get(id=id)

    serializer = LevelSerializer(level)

    data = {"level": serializer.data}

    return JsonResponse(data, safe=False)


def sublevels_list(request):
    """
    Retrieve a list of all sublevels and return them as a JSON response.

    This view fetches all Sublevel objects, serializes them using the
    SublevelSerializer, and returns the serialized data as a JSON response.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.

    Returns
    -------
    JsonResponse
        A JSON response containing the list of serialized sublevels.
    """
    sublevels = Sublevel.objects.all()

    serializer = SublevelSerializer(sublevels, many=True)

    data = {
        "sublevels": serializer.data,
    }

    return JsonResponse(data, safe=False)
