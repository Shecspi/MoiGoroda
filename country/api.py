"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django.db.models import Count, Q, QuerySet
from rest_framework import generics, status
import rest_framework.exceptions as drf_exc
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from country.models import Country, VisitedCountry, PartOfTheWorld, Location
from country.serializers import (
    CountrySerializer,
    VisitedCountrySerializer,
    PartOfTheWorldSerializer,
    LocationSerializer,
    CountrySimpleSerializer,
)
from services import logger


class GetPartsOfTheWorld(generics.ListAPIView):  # type: ignore[type-arg]
    queryset = PartOfTheWorld.objects.all()  # type: ignore[assignment]
    http_method_names = ['get']
    serializer_class = PartOfTheWorldSerializer


class GetLocations(generics.ListAPIView):  # type: ignore[type-arg]
    queryset = Location.objects.all()  # type: ignore[assignment]
    http_method_names = ['get']
    serializer_class = LocationSerializer


class GetAllCountry(generics.ListAPIView):  # type: ignore[type-arg]
    queryset = Country.objects.all()  # type: ignore[assignment]
    http_method_names = ['get']
    serializer_class = CountrySerializer

    def get(self, *args: Any, **kwargs: Any) -> Response:
        from_page = (
            self.request.GET.get('from') if self.request.GET.get('from') else 'unknown location'
        )

        logger.info(
            self.request,
            f'(API: Country): Successful request for a list of all countries from {from_page}',
        )
        return super().get(*args, **kwargs)


class GetVisitedCountry(generics.ListAPIView):  # type: ignore[type-arg]
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    serializer_class = VisitedCountrySerializer

    def get(self, *args: Any, **kwargs: Any) -> Response:
        from_page = (
            self.request.GET.get('from') if self.request.GET.get('from') else 'unknown location'
        )

        logger.info(
            self.request,
            f'(API: Country): Successful request for a list of visited countries from {from_page}',
        )
        return super().get(*args, **kwargs)

    def get_queryset(self) -> QuerySet[VisitedCountry]:  # type: ignore[override]
        return VisitedCountry.objects.filter(user=self.request.user)  # type: ignore[misc]


class AddVisitedCountry(generics.CreateAPIView):  # type: ignore[type-arg]
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]
    serializer_class = VisitedCountrySerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        from_page = request.data.get('from') if request.data.get('from') else 'unknown location'

        serializer = VisitedCountrySerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            logger.warning(
                self.request,
                f'(API: Add visited country) Validation in the serializer failed from {from_page}. {serializer.errors}',
            )
            raise drf_exc.ValidationError(serializer.errors)

        serializer.save(user=request.user)

        logger.info(
            self.request,
            f'(API: Country): The visited country has been successfully added from {from_page}',
        )

        return Response({'status': 'success', 'country': serializer.data})


class DeleteVisitedCountry(generics.DestroyAPIView):  # type: ignore[type-arg]
    http_method_names = ['delete']
    permission_classes = [IsAuthenticated]
    serializer_class = VisitedCountrySerializer

    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        from_page = request.data.get('from') if request.data.get('from') else 'unknown location'
        code_value = kwargs.get('code')
        code = code_value.upper() if code_value else ''

        try:
            country = Country.objects.get(code=code)
        except Country.DoesNotExist:
            logger.warning(
                self.request,
                f"(API: Country): Country with code '{code}' not found from {from_page}",
            )
            raise drf_exc.NotFound(f"Country with code '{code}' not found")

        # В таблице VisitedCountry не должно быть больше одного элемента
        # с одинаковыми полями user и country, поэтому дополнительную проверку на это можно не делать.
        visited_country = VisitedCountry.objects.filter(user=request.user, country=country)  # type: ignore[misc]

        # delete() к несуществующей записи не создаёт исключений, поэтому обработка исключений не требуется
        visited_country.delete()

        logger.info(
            self.request,
            f'(API: Country): The visited country has been successfully deleted from {from_page}',
        )

        return Response(status=204)


class RecieveUnknownCountries(generics.GenericAPIView):  # type: ignore[type-arg]
    def post(self, *args: Any, **kwargs: Any) -> Response:
        logger.warning(
            self.request,
            f'(API Country) Difference between lists of countries in Yandex and local DB. Unknown countries from '
            f'Yandex: {self.request.POST.get("unknown_from_yandex")}. Unknown countries from local DB: '
            f'{self.request.POST.get("unknown_to_yandex")}.',
        )

        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def country_list_with_visited_cities(request: Request) -> Response:
    """
    Возвращает список стран.
    Для авторизованного пользователя - все посещённые.
    Дл неавторизованного - все страны, у которых есть города.
    """
    if request.user.is_authenticated:
        queryset = (
            Country.objects.filter(city__isnull=False)
            .annotate(
                number_of_visited_cities=Count(
                    'city',
                    filter=Q(city__visitedcity__user=request.user),
                    distinct=True,
                ),
                number_of_cities=Count('city', distinct=True),
            )
            .order_by(
                '-number_of_visited_cities',  # сначала страны с посещёнными городами
                'name',  # затем сортировка по имени страны
            )
            .distinct()
        )
    else:
        queryset = Country.objects.filter(city__isnull=False).distinct().order_by('name')  # type: ignore[assignment]
    serializer = CountrySimpleSerializer(queryset, many=True)
    return Response(serializer.data)
