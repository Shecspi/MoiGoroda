# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

import json
import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Any, cast

from django.contrib.auth.models import User
from dmr import Controller, ResponseSpec, modify
from dmr.plugins.msgspec import MsgspecSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from place.models import Place, Category, PlaceCollection
from place.schemas import CategoryItem, PlaceCollectionItem, PlaceItem, TagOSMItem
from place.serializers import (
    PlaceSerializer,
    CategorySerializer,
    PlaceCollectionSerializer,
)
from services import logger


def _format_datetime(value: datetime) -> str:
    value_as_string = value.isoformat()
    if value_as_string.endswith('+00:00'):
        return f'{value_as_string[:-6]}Z'
    return value_as_string


def _serialize_place(place: Place) -> PlaceItem:
    collection = place.collection
    return PlaceItem(
        id=place.id,
        name=place.name,
        latitude=place.latitude,
        longitude=place.longitude,
        category_detail=CategoryItem(
            id=place.category.id,
            name=place.category.name,
            tags_detail=[TagOSMItem(id=tag.id, name=tag.name) for tag in place.category.tags.all()],
        ),
        created_at=_format_datetime(place.created_at),
        updated_at=_format_datetime(place.updated_at),
        is_visited=place.is_visited,
        collection_detail=(
            PlaceCollectionItem(
                id=str(collection.id),
                title=collection.title,
                is_public=collection.is_public,
                user=collection.user_id,
            )
            if collection is not None
            else None
        ),
    )


class GetCategory(generics.ListAPIView[Category]):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('name')  # type: ignore[assignment]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info(
            request,
            '(API: Place): Getting a list of categories',
        )
        return super(GetCategory, self).get(request, *args, **kwargs)


class GetPlaces(Controller[MsgspecSerializer]):
    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(dict[str, str], status_code=HTTPStatus.FORBIDDEN),
        ],
        tags=['Места'],
    )
    def get(self) -> Any:
        request = self.request
        logger.info(
            request,
            '(API: Place): Getting a list of places',
        )

        queryset = self.get_queryset()
        if queryset is None:
            return self.to_response(
                raw_data={'detail': 'Необходима авторизация.'},
                status_code=HTTPStatus.FORBIDDEN,
            )
        data = [_serialize_place(place) for place in queryset]
        return self.to_response(raw_data=data, status_code=HTTPStatus.OK)

    def get_queryset(self) -> Any:
        request = self.request
        collection_uuid_raw = request.GET.get('collection', '').strip()
        visited_only = request.GET.get('visited_only', '').lower() in ('true', '1', 'yes')

        if not collection_uuid_raw:
            if not request.user.is_authenticated:
                return None
            qs = Place.objects.filter(user=request.user)
        else:
            try:
                collection_uuid = uuid.UUID(collection_uuid_raw)
            except (ValueError, TypeError):
                return Place.objects.none()

            collection = PlaceCollection.objects.filter(pk=collection_uuid).first()

            if collection is None:
                return Place.objects.none()

            if not collection.is_public:
                if not request.user.is_authenticated or request.user != collection.user:
                    return Place.objects.none()

            # Владельцу отдаём все его места: можно переключаться между коллекциями и редактировать их,
            # по умолчанию отображается выбранная коллекция на фронте.
            if request.user.is_authenticated and request.user == collection.user:
                qs = Place.objects.filter(user=request.user)
            else:
                qs = Place.objects.filter(collection=collection)

        if visited_only:
            qs = qs.filter(is_visited=True)
        return qs.select_related('category', 'collection').prefetch_related('category__tags')


class GetPlaceCollections(generics.ListAPIView[PlaceCollection]):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    serializer_class = PlaceCollectionSerializer

    def get_queryset(self) -> Any:
        return PlaceCollection.objects.filter(user=cast(User, self.request.user)).order_by(
            '-created_at'
        )

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info(
            request,
            '(API: Place): Getting a list of place collections',
        )
        return super(GetPlaceCollections, self).get(request, *args, **kwargs)


class CreatePlaceCollection(generics.CreateAPIView[PlaceCollection]):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    serializer_class = PlaceCollectionSerializer

    def perform_create(self, serializer: BaseSerializer[PlaceCollection]) -> None:
        instance = serializer.save(user=cast(User, self.request.user))
        logger.info(
            self.request,
            f'(API: Place): Creation of place collection #{instance.id}',
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super(CreatePlaceCollection, self).post(request, *args, **kwargs)


class UpdatePlaceCollection(generics.UpdateAPIView[PlaceCollection]):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['patch', 'delete']
    serializer_class = PlaceCollectionSerializer

    def get_queryset(self) -> Any:
        return PlaceCollection.objects.filter(user=cast(User, self.request.user))

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().update(request, *args, **kwargs)
        logger.info(
            request,
            f'(API: Place): Updating place collection {kwargs["pk"]}',
        )
        return response

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        collection = self.get_object()
        delete_places = False
        if request.content_type and 'application/json' in request.content_type and request.body:
            try:
                body = json.loads(request.body)
                delete_places = body.get('delete_places') is True
            except (ValueError, TypeError):
                pass

        collection_id = collection.id
        places_in_collection = Place.objects.filter(
            collection=collection, user=cast(User, request.user)
        )

        if delete_places:
            places_in_collection.delete()
        else:
            places_in_collection.update(collection=None)

        collection.delete()

        logger.info(
            request,
            f'(API: Place): Deleted place collection {collection_id}, delete_places={delete_places}',
        )

        return Response(status=204)


class CreatePlace(generics.CreateAPIView[Place]):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']
    serializer_class = PlaceSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super(CreatePlace, self).post(request, *args, **kwargs)

    def perform_create(self, serializer: BaseSerializer[Place]) -> None:
        instance = serializer.save()
        logger.info(
            self.request,
            f'(API: Place): Creation of the place #{instance.id}',
        )


class DeletePlace(generics.DestroyAPIView[Place]):
    """
    Удаление места. get_queryset фильтрует по user — пользователь может удалять только свои места.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete']

    def get_queryset(self) -> Any:
        return Place.objects.filter(user=cast(User, self.request.user))

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info(
            request,
            f'(API: Place): Deleting a place #{kwargs["pk"]}',
        )
        return super(DeletePlace, self).delete(request, *args, **kwargs)


class UpdatePlace(generics.UpdateAPIView[Place]):
    """
    Обновление места. get_queryset фильтрует по user — пользователь может редактировать только свои места.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['patch']
    serializer_class = PlaceSerializer

    def get_queryset(self) -> Any:
        return Place.objects.filter(user=cast(User, self.request.user))

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        old_place = Place.objects.get(id=kwargs['pk'])
        response = super().update(request, *args, **kwargs)
        new_place = Place.objects.get(id=kwargs['pk'])
        logger.info(
            request,
            f'(API: Place): Updating a place #{old_place.id}. Name: "{old_place.name}" -> "{new_place.name}"',
        )

        return response
