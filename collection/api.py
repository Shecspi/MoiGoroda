"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from collection.models import Collection
from collection.serializers import CollectionSearchParamsSerializer


@api_view(['GET'])
def collection_search(request: Request) -> Response:
    """
    Поиск регионов по подстроке.

    Принимает GET-параметр `query`:
      - если параметр отсутствует → возвращает 400 с сообщением об ошибке,
      - если параметр указан → ищет объекты `Collection`, у которых поле
        `title` содержит подстроку (без учёта регистра).

    Возвращает список словарей с полями:
      - `id`: int — идентификатор коллекции,
      - `title`: str — название коллекции.

    :param request: DRF Request с GET-параметрами
    :return: Response со списком коллекций или ошибкой 400
    """
    serializer = CollectionSearchParamsSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)

    query = serializer.validated_data.get('query')

    if not query:
        return Response(
            {'detail': 'Параметр query является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    regions = Collection.objects.filter(title__icontains=query).order_by('title')

    collection_list: list[dict[str, Any]] = [
        {'id': collection.id, 'title': collection.title} for collection in regions
    ]

    return Response(collection_list, status=status.HTTP_200_OK)
