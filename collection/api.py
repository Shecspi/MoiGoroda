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

from collection.models import Collection, FavoriteCollection, PersonalCollection
from collection.serializers import (
    CollectionSearchParamsSerializer,
    PersonalCollectionCreateSerializer,
    PersonalCollectionUpdatePublicStatusSerializer,
)


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
        return Response({'detail': 'Коллекция не найдена'}, status=status.HTTP_404_NOT_FOUND)

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def personal_collection_create(request: Request) -> Response:
    """
    Создаёт новую персональную коллекцию для текущего пользователя.

    Принимает JSON с полями:
    - `title`: str — название коллекции (обязательное, максимум 256 символов)
    - `city_ids`: list[int] — список ID городов для добавления в коллекцию (обязательное, не пустое)
    - `is_public`: bool — публичная ли коллекция (необязательное, по умолчанию False)

    Возвращает:
    - При успехе: 201 с полями `id` (ID созданной коллекции) и `title`
    - При ошибке валидации: 400 с описанием ошибки
    - При отсутствии авторизации: 401

    :param request: DRF Request с авторизованным пользователем
    :return: Response с результатом создания коллекции
    """
    serializer = PersonalCollectionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = cast(User, request.user)
    title = serializer.validated_data['title']
    city_ids = serializer.validated_data['city_ids']
    is_public = serializer.validated_data.get('is_public', False)

    # Проверяем существование всех городов
    from city.models import City

    cities = City.objects.filter(id__in=city_ids)
    found_city_ids = set(cities.values_list('id', flat=True))
    missing_city_ids = set(city_ids) - found_city_ids

    if missing_city_ids:
        return Response(
            {
                'detail': f'Города с ID {sorted(missing_city_ids)} не найдены',
                'missing_city_ids': sorted(missing_city_ids),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Создаём коллекцию
    collection = PersonalCollection.objects.create(
        user=user,
        title=title,
        is_public=is_public,
    )

    # Добавляем города в коллекцию
    collection.city.set(cities)

    return Response(
        {
            'id': collection.id,
            'title': collection.title,
            'is_public': collection.is_public,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def personal_collection_update(request: Request, collection_id: str) -> Response:
    """
    Обновляет персональную коллекцию.

    Принимает JSON с полями:
    - `title`: str — название коллекции (обязательное, максимум 256 символов)
    - `city_ids`: list[int] — список ID городов для добавления в коллекцию (обязательное, не пустое)
    - `is_public`: bool — публичная ли коллекция (необязательное, по умолчанию False)

    Возвращает:
    - При успехе: 200 с полями `id` (ID коллекции) и `title`
    - При ошибке валидации: 400 с описанием ошибки
    - При отсутствии авторизации: 401
    - При отсутствии коллекции: 404
    - При попытке изменить чужую коллекцию: 403

    :param request: DRF Request с авторизованным пользователем
    :param collection_id: UUID коллекции в виде строки
    :return: Response с результатом обновления коллекции
    """
    import uuid

    from collection.serializers import PersonalCollectionUpdateSerializer

    try:
        collection_uuid = uuid.UUID(collection_id)
    except ValueError:
        return Response(
            {'detail': 'Неверный формат UUID коллекции'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        collection = PersonalCollection.objects.get(id=collection_uuid)
    except PersonalCollection.DoesNotExist:
        return Response(
            {'detail': 'Коллекция не найдена'},
            status=status.HTTP_404_NOT_FOUND,
        )

    user = cast(User, request.user)
    if collection.user != user:
        return Response(
            {'detail': 'У вас нет прав на изменение этой коллекции'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = PersonalCollectionUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    title = serializer.validated_data['title']
    city_ids = serializer.validated_data['city_ids']
    is_public = serializer.validated_data.get('is_public', False)

    # Проверяем существование всех городов
    from city.models import City

    cities = City.objects.filter(id__in=city_ids)
    found_city_ids = set(cities.values_list('id', flat=True))
    missing_city_ids = set(city_ids) - found_city_ids

    if missing_city_ids:
        return Response(
            {
                'detail': f'Города с ID {sorted(missing_city_ids)} не найдены',
                'missing_city_ids': sorted(missing_city_ids),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Обновляем коллекцию
    collection.title = title
    collection.is_public = is_public
    collection.save()

    # Обновляем города в коллекции
    collection.city.set(cities)

    return Response(
        {
            'id': collection.id,
            'title': collection.title,
            'is_public': collection.is_public,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def personal_collection_update_public_status(request: Request, collection_id: str) -> Response:
    """
    Изменяет статус публичности персональной коллекции.

    Принимает JSON с полем:
    - `is_public`: bool — новый статус публичности коллекции (обязательное)

    Возвращает:
    - При успехе: 200 с полем `is_public` (новый статус)
    - При ошибке валидации: 400 с описанием ошибки
    - При отсутствии авторизации: 401
    - При отсутствии коллекции: 404
    - При попытке изменить чужую коллекцию: 403

    :param request: DRF Request с авторизованным пользователем
    :param collection_id: UUID персональной коллекции
    :return: Response с результатом изменения статуса
    """
    import uuid

    try:
        collection_uuid = uuid.UUID(collection_id)
    except ValueError:
        return Response(
            {'detail': 'Неверный формат UUID коллекции'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Проверяем существование коллекции
    try:
        collection = PersonalCollection.objects.get(id=collection_uuid)
    except ObjectDoesNotExist:
        return Response(
            {'detail': 'Коллекция не найдена'},
            status=status.HTTP_404_NOT_FOUND,
        )

    user = cast(User, request.user)

    # Проверяем, что пользователь является создателем коллекции
    if collection.user != user:
        return Response(
            {'detail': 'Вы не можете изменять эту коллекцию'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = PersonalCollectionUpdatePublicStatusSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    is_public = serializer.validated_data['is_public']
    collection.is_public = is_public
    collection.save(update_fields=['is_public'])

    return Response(
        {'is_public': collection.is_public},
        status=status.HTTP_200_OK,
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def personal_collection_delete(request: Request, collection_id: str) -> Response:
    """
    Удаляет персональную коллекцию.

    Возвращает:
    - При успехе: 204 No Content
    - При отсутствии авторизации: 401
    - При отсутствии коллекции: 404
    - При попытке удалить чужую коллекцию: 403

    :param request: DRF Request с авторизованным пользователем
    :param collection_id: UUID персональной коллекции
    :return: Response с результатом удаления
    """
    import uuid

    try:
        collection_uuid = uuid.UUID(collection_id)
    except ValueError:
        return Response(
            {'detail': 'Неверный формат UUID коллекции'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Проверяем существование коллекции
    try:
        collection = PersonalCollection.objects.get(id=collection_uuid)
    except ObjectDoesNotExist:
        return Response(
            {'detail': 'Коллекция не найдена'},
            status=status.HTTP_404_NOT_FOUND,
        )

    user = cast(User, request.user)

    # Проверяем, что пользователь является создателем коллекции
    if collection.user != user:
        return Response(
            {'detail': 'Вы не можете удалить эту коллекцию'},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Удаляем коллекцию
    collection.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
