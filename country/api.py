"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.db.models import Count, Q
from rest_framework import generics
import rest_framework.exceptions as drf_exc
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
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


class GetPartsOfTheWorld(generics.ListAPIView):
    queryset = PartOfTheWorld.objects.all()
    http_method_names = ['get']
    serializer_class = PartOfTheWorldSerializer


class GetLocations(generics.ListAPIView):
    queryset = Location.objects.all()
    http_method_names = ['get']
    serializer_class = LocationSerializer


class GetAllCountry(generics.ListAPIView):
    queryset = Country.objects.all()
    http_method_names = ['get']
    serializer_class = CountrySerializer

    def get(self, *args, **kwargs):
        from_page = (
            self.request.GET.get('from') if self.request.GET.get('from') else 'unknown location'
        )

        logger.info(
            self.request,
            f'(API: Country): Successful request for a list of all countries from {from_page}',
        )
        return super().get(self, *args, **kwargs)


class GetVisitedCountry(generics.ListAPIView):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    serializer_class = VisitedCountrySerializer

    def get(self, *args, **kwargs):
        from_page = (
            self.request.GET.get('from') if self.request.GET.get('from') else 'unknown location'
        )

        logger.info(
            self.request,
            f'(API: Country): Successful request for a list of visited countries from {from_page}',
        )
        return super().get(self, *args, **kwargs)

    def get_queryset(self):
        return VisitedCountry.objects.filter(user=self.request.user)


class AddVisitedCountry(generics.CreateAPIView):
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]
    serializer_class = VisitedCountrySerializer

    def post(self, request, *args, **kwargs):
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


class DeleteVisitedCountry(generics.DestroyAPIView):
    http_method_names = ['delete']
    permission_classes = [IsAuthenticated]
    serializer_class = VisitedCountrySerializer

    def delete(self, request, *args, **kwargs):
        from_page = request.data.get('from') if request.data.get('from') else 'unknown location'
        code = kwargs.get('code').upper()

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
        visited_country = VisitedCountry.objects.filter(user=request.user, country=country)

        # delete() к несуществующей записи не создаёт исключений, поэтому обработка исключений не требуется
        visited_country.delete()

        logger.info(
            self.request,
            f'(API: Country): The visited country has been successfully deleted from {from_page}',
        )

        return Response(status=204)


class RecieveUnknownCountries(generics.GenericAPIView):
    def post(self, *args, **kwargs):
        logger.warning(
            self.request,
            f'(API Country) Difference between lists of countries in Yandex and local DB. Unknown countries from '
            f'Yandex: {self.request.POST.get('unknown_from_yandex')}. Unknown countries from local DB: '
            f'{self.request.POST.get('unknown_to_yandex')}.',
        )

        return Response(status=200)


@api_view(['GET'])
def country_list_with_visited_cities(request):
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
        queryset = Country.objects.filter(city__isnull=False).distinct().order_by('name')
    serializer = CountrySimpleSerializer(queryset, many=True)
    return Response(serializer.data)
