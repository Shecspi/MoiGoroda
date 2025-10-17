"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any, cast

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from collection.models import Collection, FavoriteCollection
from collection.serializers import CollectionSearchParamsSerializer


@api_view(['GET'])
def collection_search(request: Request) -> Response:
    """
    Поиск коллекций по подстроке.

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

    collections = Collection.objects.filter(title__icontains=query).order_by('title')

    collection_list: list[dict[str, Any]] = [
        {'id': collection.id, 'title': collection.title} for collection in collections
    ]

    return Response(collection_list, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_collection_toggle(request: Request, collection_id: int) -> Response:
    """
    Добавляет или удаляет коллекцию из избранного пользователя.

    POST - добавить коллекцию в избранное
    DELETE - удалить коллекцию из избранного

    :param request: DRF Request с авторизованным пользователем
    :param collection_id: ID коллекции
    :return: Response с результатом операции
    """
    # Проверяем существование коллекции
    try:
        collection = Collection.objects.get(id=collection_id)
    except ObjectDoesNotExist:
        return Response(
            {'detail': 'Коллекция не найдена'}, status=status.HTTP_404_NOT_FOUND
        )

    user = cast(User, request.user)

    if request.method == 'POST':
        # Добавление в избранное
        if FavoriteCollection.objects.filter(user=user, collection=collection).exists():
            return Response(
                {'detail': 'Коллекция уже находится в избранном'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        FavoriteCollection.objects.create(user=user, collection=collection)
        return Response({'is_favorite': True}, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        # Удаление из избранного
        try:
            favorite = FavoriteCollection.objects.get(user=user, collection=collection)
            favorite.delete()
            return Response({'is_favorite': False}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {'detail': 'Коллекция не находится в избранном'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(
        {'detail': 'Метод не поддерживается'}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )
