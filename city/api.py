"""
Реализует API для получения информации о посещённых и непосещённых городах.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django.contrib.auth.models import User
import rest_framework.exceptions as drf_exc
from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from account.models import ShareSettings
from city.models import City, VisitedCity
from city.serializers import (
    AddVisitedCitySerializer,
    CitySearchParamsSerializer,
    CitySerializer,
    NotVisitedCitySerializer,
    VisitedCitySerializer,
)
from city.services.db import (
    get_first_visit_date_by_city,
    get_last_visit_date_by_city,
    get_not_visited_cities,
    get_number_of_visits_by_city,
    get_unique_visited_cities,
)
from city.services.filter import apply_filter_to_queryset
from city.services.search import CitySearchService
from services import logger
from subscribe.repository import is_subscribed


class GetVisitedCities(generics.ListAPIView):  # type: ignore[type-arg]
    serializer_class = VisitedCitySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get(self, *args: Any, **kwargs: Any) -> Response:
        user = self.request.user
        user_id = user.id if isinstance(user, User) else None
        logger.info(
            self.request,
            f'(API) Successful request for a list of visited cities (user #{user_id})',
        )

        return super().get(*args, **kwargs)

    def get_queryset(self) -> QuerySet[VisitedCity]:
        user_id = self.request.user.pk
        if user_id is None:
            return VisitedCity.objects.none()

        country_id = self.request.GET.get('country')
        filter = self.request.GET.get('filter')

        queryset = get_unique_visited_cities(user_id, country_id)

        if filter:
            queryset = apply_filter_to_queryset(queryset, user_id, filter)

        return queryset


class GetVisitedCitiesFromSubscriptions(generics.ListAPIView):  # type: ignore[type-arg]
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
            current_user = self.request.user
            current_user_id = current_user.id if isinstance(current_user, User) else None
            logger.warning(
                self.request,
                f'(API) Attempt to get a list of the cities of a user who did not change initial settings '
                f'(from #{current_user_id}, to #{user_id})',
            )
        else:
            if user_settings.can_subscribe:
                return True
            else:
                current_user = self.request.user
                current_user_id = current_user.id if isinstance(current_user, User) else None
                logger.warning(
                    self.request,
                    f'(API) Attempt to get a list of the cities of a user who did not allow it '
                    f'(from #{current_user_id}, to #{user_id})',
                )
        return False

    def _is_subscription_exists(self, to_id: int) -> bool:
        from_id = self.request.user.pk
        if from_id is None:
            return False
        if is_subscribed(from_id, to_id):
            return True
        else:
            current_user = self.request.user
            current_user_id = current_user.id if isinstance(current_user, User) else None
            logger.warning(
                self.request,
                f'(API) Attempt to get a list of the cities of a user for whom do not have a subscription '
                f'(from #{current_user_id}, to #{to_id})',
            )
            return False

    def get(self, *args: Any, **kwargs: Any) -> Response:
        user_ids_str = self.request.GET.getlist('user_ids')

        try:
            user_ids = [int(user_id) for user_id in user_ids_str]
        except ValueError:
            logger.warning(
                self.request,
                '(API) Received invalid user_ids, cannot cast to int',
            )
            raise drf_exc.ParseError('Получен некорректный список идентификаторов пользователей')

        user = self.request.user
        is_superuser = user.is_superuser if isinstance(user, User) else False
        if not is_superuser:
            # Убираем из списка ID тех пользователей, которые не разрешили подписываться на себя.
            # Вообще это нештатная ситуация, но теоритически возможная, когда пользователь запретил
            # подписываться после того, как была открыта страница с картой, но до того, как запрос пришёл на сервер.
            for user_id in user_ids:
                if self._user_has_allowed_to_subscribe_to_himself(
                    user_id
                ) and self._is_subscription_exists(user_id):
                    self.user_ids.append(user_id)
                    current_user_id = user.id if isinstance(user, User) else None
                    logger.info(
                        self.request,
                        f'(API) Successful request for a list of visited cities from subscriptions '
                        f'(from #{current_user_id}, to #{user_id})',
                    )
        else:
            self.user_ids = user_ids

            current_user_id = user.id if isinstance(user, User) else None
            logger.info(
                self.request,
                f'(API) Successful request from superuser for a list of visited cities from subscriptions (user #{current_user_id})',
            )

        return super().get(*args, **kwargs)

    def get_queryset(self) -> QuerySet[VisitedCity]:
        if not self.user_ids:
            return VisitedCity.objects.none()
        country_id = self.request.GET.get('country')

        # get_all_visited_cities работает с одним user_id, поэтому она вызывается
        # несколько раз и результаты собираются в один QuerySet.
        querysets = [get_unique_visited_cities(user_id, country_id) for user_id in self.user_ids]
        combined_queryset = querysets[0]
        for qs in querysets[1:]:
            combined_queryset = combined_queryset.union(qs)
        return combined_queryset


class GetNotVisitedCities(generics.ListAPIView):  # type: ignore[type-arg]
    serializer_class = NotVisitedCitySerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get(self, *args: Any, **kwargs: Any) -> Response:
        user = self.request.user
        user_id = user.id if isinstance(user, User) else None
        logger.info(
            self.request,
            f'(API) Successful request for a list of not visited cities (user #{user_id})',
        )
        return super().get(*args, **kwargs)

    def get_queryset(self) -> QuerySet[City]:  # type: ignore[override]
        user_pk = self.request.user.pk
        if user_pk is None:
            return City.objects.none()
        country_code = self.request.GET.get('country')
        return get_not_visited_cities(user_pk, country_code)


class AddVisitedCity(generics.CreateAPIView):  # type: ignore[type-arg]
    serializer_class = AddVisitedCitySerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
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

        if VisitedCity.objects.filter(user=user, city=city, date_of_visit=date_of_visit).exists():  # type: ignore[misc]
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

        user_id = user.id if isinstance(user, User) else None
        if user_id is None:
            raise drf_exc.PermissionDenied('User must be authenticated')

        return_data['number_of_visits'] = get_number_of_visits_by_city(
            city_id=city.id, user_id=user_id
        )
        return_data['first_visit_date'] = get_first_visit_date_by_city(
            city_id=city.id, user_id=user_id
        )
        return_data['last_visit_date'] = get_last_visit_date_by_city(
            city_id=city.id, user_id=user_id
        )

        return Response({'status': 'success', 'city': return_data})


@api_view(['GET'])
def city_list_by_region(request: Request) -> Response:
    region_id = request.GET.get('region_id')
    if not region_id:
        return Response(
            {'detail': 'Параметр region_id является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cities = City.objects.filter(region_id=region_id).order_by('title')
    serializer = CitySerializer(cities, many=True, context={'request': request})  # type: ignore[arg-type]

    return Response(serializer.data)


@api_view(['GET'])
def city_list_by_country(request: Request) -> Response:
    country_id = request.GET.get('country_id')
    if not country_id:
        return Response(
            {'detail': 'Параметр country_id является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cities = City.objects.filter(country_id=country_id).order_by('title')
    serializer = CitySerializer(cities, many=True, context={'request': request})  # type: ignore[arg-type]

    return Response(serializer.data)


@api_view(['GET'])
def city_search(request: Request) -> Response:
    """
    Поиск городов по подстроке.

    Принимает GET-параметры:
      - query (обязательный): подстрока для поиска в названии города
      - country (необязательный): код страны для дополнительной фильтрации
      - limit (необязательный): максимальное количество результатов (по умолчанию 50, максимум 200)

    Возвращает список городов с полями id, title, region и country.
    Результаты отсортированы по приоритету (города, начинающиеся с запроса, идут первыми).

    :param request: DRF Request с GET-параметрами
    :return: Response со списком городов или ошибкой валидации
    """
    # Валидация входных данных
    serializer = CitySearchParamsSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data
    query = validated_data['query']
    country = validated_data.get('country')
    limit = validated_data.get('limit', 50)

    # Поиск городов через сервис
    cities_queryset = CitySearchService.search_cities(query=query, country=country, limit=limit)

    # Использование сериализатора для формирования ответа
    city_serializer = CitySerializer(cities_queryset, many=True, context={'request': request})  # type: ignore[arg-type]

    return Response(city_serializer.data, status=status.HTTP_200_OK)
