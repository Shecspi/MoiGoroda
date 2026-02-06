from typing import Any, cast
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from place.models import Place, Category, PlaceCollection
from place.serializers import (
    PlaceSerializer,
    CategorySerializer,
    PlaceCollectionSerializer,
)
from services import logger


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


class GetPlaces(generics.ListAPIView[Place]):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    serializer_class = PlaceSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        logger.info(
            request,
            '(API: Place): Getting a list of places',
        )
        return super(GetPlaces, self).get(request, *args, **kwargs)

    def get_queryset(self) -> Any:
        return Place.objects.filter(user=cast(User, self.request.user))


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
    http_method_names = ['patch']
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
