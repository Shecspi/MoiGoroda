"""
Реализует API для получения информации о посещённых и непосещённых городах.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
import rest_framework.exceptions as drf_exc
from rest_framework.response import Response

from account.models import ShareSettings
from city.models import City, VisitedCity
from city.serializers import (
    VisitedCitySerializer,
    NotVisitedCitySerializer,
    AddVisitedCitySerializer,
    CitySerializer,
)
from city.services.filter import apply_filter_to_queryset
from services import logger
from city.services.db import (
    get_unique_visited_cities,
    get_number_of_visits_by_city,
    get_first_visit_date_by_city,
    get_last_visit_date_by_city,
    get_not_visited_cities,
)
from subscribe.repository import is_subscribed


class GetVisitedCities(generics.ListAPIView):
    serializer_class = VisitedCitySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get(self, *args, **kwargs):
        logger.info(
            self.request,
            f'(API) Successful request for a list of visited cities (user #{self.request.user.id})',
        )

        return super().get(*args, **kwargs)

    def get_queryset(self):
        user_id = self.request.user.pk
        country_id = self.request.GET.get('country')
        filter = self.request.GET.get('filter')

        queryset = get_unique_visited_cities(user_id, country_id)

        if filter:
            queryset = apply_filter_to_queryset(queryset, user_id, filter)

        return queryset


class GetVisitedCitiesFromSubscriptions(generics.ListAPIView):
    serializer_class = VisitedCitySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def __init__(self) -> None:
        # Список ID пользователей, у которых необходимо вернуть посещённые города
        self.user_ids: list[int] = []

        super().__init__()

    def _user_has_allowed_to_subscribe_to_himself(self, user_id: int) -> bool:
        try:
            user_settings = ShareSettings.objects.get(user_id=user_id)
        except ShareSettings.DoesNotExist:
            logger.warning(
                self.request,
                f'(API) Attempt to get a list of the cities of a user who did not change initial settings '
                f'(from #{self.request.user.id}, to #{user_id})',
            )
        else:
            if user_settings.can_subscribe:
                return True
            else:
                logger.warning(
                    self.request,
                    f'(API) Attempt to get a list of the cities of a user who did not allow it '
                    f'(from #{self.request.user.id}, to #{user_id})',
                )
        return False

    def _is_subscription_exists(self, to_id: int) -> bool:
        from_id = self.request.user.pk
        if is_subscribed(from_id, to_id):
            return True
        else:
            logger.warning(
                self.request,
                f'(API) Attempt to get a list of the cities of a user for whom do not have a subscription '
                f'(from #{from_id}, to #{to_id})',
            )
            return False

    def get(self, *args, **kwargs):
        user_ids = self.request.GET.getlist('user_ids')

        try:
            user_ids = [int(user_id) for user_id in user_ids]
        except ValueError:
            logger.warning(
                self.request,
                '(API) Received invalid user_ids, cannot cast to int',
            )
            raise drf_exc.ParseError('Получен некорректный список идентификаторов пользователей')

        if not self.request.user.is_superuser:
            # Убираем из списка ID тех пользователей, которые не разрешили подписываться на себя.
            # Вообще это нештатная ситуация, но теоритически возможная, когда пользователь запретил
            # подписываться после того, как была открыта страница с картой, но до того, как запрос пришёл на сервер.
            for user_id in user_ids:
                if self._user_has_allowed_to_subscribe_to_himself(
                    user_id
                ) and self._is_subscription_exists(user_id):
                    self.user_ids.append(user_id)
                    logger.info(
                        self.request,
                        f'(API) Successful request for a list of visited cities from subscriptions '
                        f'(from #{self.request.user.id}, to #{user_id})',
                    )
        else:
            self.user_ids = user_ids

            logger.info(
                self.request,
                f'(API) Successful request from superuser for a list of visited cities from subscriptions (user #{self.request.user.id})',
            )

        return super().get(*args, **kwargs)

    def get_queryset(self):
        if not self.user_ids:
            return []
        country_id = self.request.GET.get('country')

        # get_all_visited_cities работает с одним user_id, поэтому она вызывается
        # несколько раз и результаты собираются в один QuerySet.
        querysets = [get_unique_visited_cities(user_id, country_id) for user_id in self.user_ids]
        combined_queryset = querysets[0]
        for qs in querysets[1:]:
            combined_queryset = combined_queryset.union(qs)
        return combined_queryset


class GetNotVisitedCities(generics.ListAPIView):
    serializer_class = NotVisitedCitySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get(self, *args, **kwargs):
        logger.info(
            self.request,
            f'(API) Successful request for a list of not visited cities (user #{self.request.user.id})',
        )
        return super().get(*args, **kwargs)

    def get_queryset(self):
        country_code = self.request.GET.get('country')
        print(country_code)
        return get_not_visited_cities(self.request.user.pk, country_code)


class AddVisitedCity(generics.CreateAPIView):
    serializer_class = AddVisitedCitySerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        from_page = request.data.get('from') if request.data.get('from') else 'unknown location'

        serializer = AddVisitedCitySerializer(data=request.data, context={'request': self.request})
        if not serializer.is_valid():
            logger.warning(
                self.request,
                f'(API: Add visited city) Validation in the serializer failed from {from_page}',
            )
            raise drf_exc.ValidationError(serializer.errors)

        user = request.user
        city = City.objects.get(id=serializer.validated_data['city'].id)
        date_of_visit = serializer.validated_data['date_of_visit']

        if VisitedCity.objects.filter(user=user, city=city, date_of_visit=date_of_visit).exists():
            return Response(
                {
                    'status': 'success',
                    'message': f'Вы уже сохранили посещение города {city} {date_of_visit}',
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer.save(user=user)

        logger.info(
            self.request,
            f'(API: Add visited city) The visited city has been successfully added from {from_page}',
        )
        return_data = dict(serializer.data)
        return_data['number_of_visits'] = get_number_of_visits_by_city(
            city_id=city.id, user_id=user.id
        )
        return_data['first_visit_date'] = get_first_visit_date_by_city(
            city_id=city.id, user_id=user.id
        )
        return_data['last_visit_date'] = get_last_visit_date_by_city(
            city_id=city.id, user_id=user.id
        )

        return Response({'status': 'success', 'city': return_data})


@api_view(['GET'])
def city_list_by_region(request):
    region_id = request.GET.get('region_id')
    if not region_id:
        return Response(
            {'detail': 'Параметр region_id является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cities = City.objects.filter(region_id=region_id).order_by('title')
    serializer = CitySerializer(cities, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def city_list_by_country(request):
    country_id = request.GET.get('country_id')
    if not country_id:
        return Response(
            {'detail': 'Параметр country_id является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cities = City.objects.filter(country_id=country_id).order_by('title')
    serializer = CitySerializer(cities, many=True)

    return Response(serializer.data)
