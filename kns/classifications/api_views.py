"""
Views for the `classifications` apis app.
"""

from django.http import JsonResponse

from .models import Classification, Subclassification
from .serializers import ClassificationSerializer, SubclassificationSerializer


def classifications_list(request):
    """
    Retrieve a list of all classifications and return them as a JSON response.

    This view fetches all Classification objects, serializes them using the
    ClassificationSerializer, and returns the serialized data as a JSON response.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.

    Returns
    -------
    JsonResponse
        A JSON response containing the list of serialized classifications.
    """
    # Get all classifications
    classifications = Classification.objects.all()

    # Serialize classifications
    serializer = ClassificationSerializer(classifications, many=True)

    # Return them as json response
    data = {
        "classifications": serializer.data,
    }

    return JsonResponse(data, safe=False)


def classification_detail(request, id):
    """
    Retrieve the details of a specific classification by its ID and return them as a JSON response.

    This view fetches a Classification object by its ID, serializes it using the
    ClassificationSerializer, and returns the serialized data as a JSON response.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    id : int
        The ID of the classification to retrieve.

    Returns
    -------
    JsonResponse
        A JSON response containing the serialized classification data.
    """
    classification = Classification.objects.get(id=id)

    serializer = ClassificationSerializer(classification)

    data = {"classification": serializer.data}

    return JsonResponse(data, safe=False)


def subclassifications_list(request):
    """
    Retrieve a list of all subclassifications and return them as a JSON response.

    This view fetches all Subclassification objects, serializes them using the
    SubclassificationSerializer, and returns the serialized data as a JSON response.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.

    Returns
    -------
    JsonResponse
        A JSON response containing the list of serialized subclassifications.
    """
    subclassifications = Subclassification.objects.all()

    # Serialize subclassifications
    serializer = SubclassificationSerializer(
        subclassifications,
        many=True,
    )

    # Return them as json response
    data = {
        "subclassifications": serializer.data,
    }

    return JsonResponse(data, safe=False)
