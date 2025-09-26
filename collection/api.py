from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from collection.models import Collection
from collection.serializers import CollectionSearchParamsSerializer


@api_view(['GET'])
def search_region(request) -> Response:
    serializer = CollectionSearchParamsSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)

    query = serializer.validated_data.get('query')

    if not query:
        return Response(
            {'detail': 'Параметр query является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    regions = Collection.objects.filter(title__icontains=query).order_by('title')

    collection_list = [{'id': collection.id, 'title': collection.title} for collection in regions]

    return Response(collection_list, status=status.HTTP_200_OK)
