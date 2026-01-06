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
from django.db.models.functions import ExtractYear
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from account.models import ShareSettings
from city.models import City, CityListDefaultSettings, VisitedCity
from city.serializers import (
    AddVisitedCitySerializer,
    CitySearchParamsSerializer,
    CitySerializer,
    NotVisitedCitySerializer,
    VisitedCitySerializer,
)
from country.models import Country
from city.services.db import (
    get_first_visit_date_by_city,
    get_last_visit_date_by_city,
    get_not_visited_cities,
    get_number_of_users_who_visit_city,
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

    def get_queryset(self) -> QuerySet[City, City]:  # type: ignore[override]
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
        return_data['number_of_users_who_visit_city'] = get_number_of_users_who_visit_city(
            city_id=city.id
        )
        return_data['number_of_visits_all_users'] = VisitedCity.objects.filter(city=city).count()

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
def city_list_by_regions(request: Request) -> Response:
    """
    Возвращает список городов для одного или нескольких регионов и/или стран.

    Принимает параметры:
    - region_ids (несколько ID через запятую): для загрузки городов по регионам
    - country_ids (несколько ID через запятую): для загрузки городов по странам без регионов

    Возвращает список городов с полями id, title, lat, lon, region, country, regionId, countryCode.

    :param request: DRF Request
    :return: Response со списком городов
    """
    region_ids_param = request.GET.get('region_ids')
    country_ids_param = request.GET.get('country_ids')

    if not region_ids_param and not country_ids_param:
        return Response(
            {'detail': 'Параметр region_ids или country_ids является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Обрабатываем region_ids
    region_ids: list[int] = []
    if region_ids_param:
        try:
            region_ids = [int(id.strip()) for id in region_ids_param.split(',') if id.strip()]
        except ValueError:
            return Response(
                {'detail': 'Параметр region_ids должен содержать список числовых ID через запятую'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Обрабатываем country_ids
    country_ids: list[int] = []
    if country_ids_param:
        try:
            country_ids = [int(id.strip()) for id in country_ids_param.split(',') if id.strip()]
        except ValueError:
            return Response(
                {
                    'detail': 'Параметр country_ids должен содержать список числовых ID через запятую'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    if not region_ids and not country_ids:
        return Response(
            {'detail': 'Не указаны валидные ID регионов или стран'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Формируем запрос для получения городов
    cities_query = City.objects.select_related('region', 'country')

    if region_ids and country_ids:
        # Если указаны и регионы, и страны - объединяем условия через OR
        # Для регионов - загружаем города по регионам
        # Для стран - загружаем все города этих стран (включая те, у которых есть регионы)
        from django.db.models import Q

        cities_query = cities_query.filter(
            Q(region_id__in=region_ids) | Q(country_id__in=country_ids)
        )
    elif region_ids:
        # Только регионы
        cities_query = cities_query.filter(region_id__in=region_ids)
    else:
        # Только страны - загружаем все города этих стран
        # (включая те, у которых есть регионы, если регионы не выбраны)
        cities_query = cities_query.filter(country_id__in=country_ids)

    cities = cities_query.order_by('title')

    # Получаем информацию о посещениях для авторизованного пользователя
    user = request.user
    user_id = user.pk if user.is_authenticated else None

    # Получаем все посещённые города пользователя одним запросом для оптимизации
    visited_city_ids: set[int] = set()
    city_visits_data: dict[int, dict[str, Any]] = {}

    if user_id:
        visited_cities = (
            VisitedCity.objects.filter(user_id=user_id, city_id__in=[city.id for city in cities])
            .select_related('city')
            .order_by('city_id', 'date_of_visit')
        )

        # Группируем посещения по городам
        for visited_city in visited_cities:
            city_id = visited_city.city_id
            visited_city_ids.add(city_id)

            if city_id not in city_visits_data:
                city_visits_data[city_id] = {
                    'first_visit_date': visited_city.date_of_visit,
                    'last_visit_date': visited_city.date_of_visit,
                    'number_of_visits': 1,
                }
            else:
                # Обновляем первую и последнюю дату посещения
                if visited_city.date_of_visit:
                    if (
                        city_visits_data[city_id]['first_visit_date'] is None
                        or visited_city.date_of_visit
                        < city_visits_data[city_id]['first_visit_date']
                    ):
                        city_visits_data[city_id]['first_visit_date'] = visited_city.date_of_visit
                    if (
                        city_visits_data[city_id]['last_visit_date'] is None
                        or visited_city.date_of_visit > city_visits_data[city_id]['last_visit_date']
                    ):
                        city_visits_data[city_id]['last_visit_date'] = visited_city.date_of_visit
                city_visits_data[city_id]['number_of_visits'] += 1

    # Формируем данные вручную, чтобы включить regionId, countryCode и информацию о посещении
    cities_data = []
    for city in cities:
        city_id = city.id
        is_visited = city_id in visited_city_ids

        city_data = {
            'id': city_id,
            'title': city.title,
            'lat': str(city.coordinate_width),
            'lon': str(city.coordinate_longitude),
            'region': city.region.full_name if city.region else None,
            'country': city.country.name if city.country else None,
            'regionId': city.region.id if city.region else None,
            'countryCode': city.country.code if city.country else None,
            'isVisited': is_visited,
        }

        # Добавляем информацию о посещении, если город посещён
        if is_visited and city_id in city_visits_data:
            visits_info = city_visits_data[city_id]
            city_data['firstVisitDate'] = (
                visits_info['first_visit_date'].isoformat()
                if visits_info['first_visit_date']
                else None
            )
            city_data['lastVisitDate'] = (
                visits_info['last_visit_date'].isoformat()
                if visits_info['last_visit_date']
                else None
            )
            city_data['numberOfVisits'] = visits_info['number_of_visits']
        else:
            city_data['firstVisitDate'] = None
            city_data['lastVisitDate'] = None
            city_data['numberOfVisits'] = 0

        cities_data.append(city_data)

    return Response(cities_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def city_list_by_ids(request: Request) -> Response:
    """
    Возвращает список городов по их ID.

    Принимает параметр:
    - city_ids (несколько ID через запятую): список ID городов для загрузки

    Возвращает список городов с полями id, title, lat, lon, region, country, regionId, countryCode.

    :param request: DRF Request
    :return: Response со списком городов
    """
    city_ids_param = request.GET.get('city_ids')

    if not city_ids_param:
        return Response(
            {'detail': 'Параметр city_ids является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Обрабатываем city_ids
    city_ids: list[int] = []
    try:
        city_ids = [int(id.strip()) for id in city_ids_param.split(',') if id.strip()]
    except ValueError:
        return Response(
            {'detail': 'Параметр city_ids должен содержать список числовых ID через запятую'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not city_ids:
        return Response(
            {'detail': 'Не указаны валидные ID городов'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Загружаем города
    cities = (
        City.objects.select_related('region', 'country').filter(id__in=city_ids).order_by('title')
    )

    # Получаем информацию о посещениях для авторизованного пользователя
    user = request.user
    user_id = user.pk if user.is_authenticated else None

    visited_city_ids: set[int] = set()
    city_visits_data: dict[int, dict[str, Any]] = {}

    if user_id:
        from city.models import VisitedCity

        visited_cities = VisitedCity.objects.filter(
            user_id=user_id, city_id__in=city_ids
        ).select_related('city')

        for visited_city in visited_cities:
            city_id = visited_city.city_id
            visited_city_ids.add(city_id)

            if city_id not in city_visits_data:
                city_visits_data[city_id] = {
                    'first_visit_date': None,
                    'last_visit_date': None,
                    'number_of_visits': 0,
                }

            if visited_city.date_of_visit:
                if (
                    not city_visits_data[city_id]['first_visit_date']
                    or visited_city.date_of_visit < city_visits_data[city_id]['first_visit_date']
                ):
                    city_visits_data[city_id]['first_visit_date'] = visited_city.date_of_visit

                if (
                    not city_visits_data[city_id]['last_visit_date']
                    or visited_city.date_of_visit > city_visits_data[city_id]['last_visit_date']
                ):
                    city_visits_data[city_id]['last_visit_date'] = visited_city.date_of_visit

            city_visits_data[city_id]['number_of_visits'] += 1

    # Формируем данные вручную, чтобы включить regionId, countryCode и информацию о посещении
    cities_data = []
    for city in cities:
        city_id = city.id
        is_visited = city_id in visited_city_ids

        city_data = {
            'id': city_id,
            'title': city.title,
            'lat': str(city.coordinate_width),
            'lon': str(city.coordinate_longitude),
            'region': city.region.full_name if city.region else None,
            'country': city.country.name if city.country else None,
            'regionId': city.region.id if city.region else None,
            'countryCode': city.country.code if city.country else None,
            'isVisited': is_visited,
        }

        # Добавляем информацию о посещении, если город посещён
        if is_visited and city_id in city_visits_data:
            visits_info = city_visits_data[city_id]
            city_data['firstVisitDate'] = (
                visits_info['first_visit_date'].isoformat()
                if visits_info['first_visit_date']
                else None
            )
            city_data['lastVisitDate'] = (
                visits_info['last_visit_date'].isoformat()
                if visits_info['last_visit_date']
                else None
            )
            city_data['numberOfVisits'] = visits_info['number_of_visits']
        else:
            city_data['firstVisitDate'] = None
            city_data['lastVisitDate'] = None
            city_data['numberOfVisits'] = 0

        cities_data.append(city_data)

    return Response(cities_data, status=status.HTTP_200_OK)


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


@api_view(['GET'])
def country_list_by_cities(request: Request) -> Response:
    """
    Возвращает список стран, у которых есть города.

    Возвращает список стран с полями id, code, name, отсортированный по названию.
    Включаются только те страны, у которых есть хотя бы один город в базе данных.

    :param request: DRF Request
    :return: Response со списком стран
    """
    # Получаем страны, у которых есть города
    countries = Country.objects.filter(city__isnull=False).distinct().order_by('name')

    # Формируем простой ответ с нужными полями
    countries_data = [
        {
            'id': country.id,
            'code': country.code,
            'name': country.name,
        }
        for country in countries
    ]

    return Response(countries_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def save_city_list_default_settings(request: Request) -> Response:
    """
    Сохраняет настройки по умолчанию фильтрации или сортировки для списка городов.

    Принимает POST-параметры:
      - parameter_type (обязательный): 'filter' или 'sort'
      - parameter_value (обязательный): значение фильтра или сортировки

    Возвращает статус успешного сохранения или ошибку валидации.

    :param request: DRF Request с POST-параметрами
    :return: Response со статусом операции
    """
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Требуется аутентификация'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    parameter_type = request.data.get('parameter_type')
    parameter_value = request.data.get('parameter_value')

    if not parameter_type or not parameter_value:
        return Response(
            {'detail': 'Параметры parameter_type и parameter_value являются обязательными'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if parameter_type not in ['filter', 'sort']:
        return Response(
            {'detail': 'parameter_type должен быть "filter" или "sort"'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Валидация значений фильтра
    if parameter_type == 'filter':
        valid_filter_values = ['no_filter', 'no_magnet', 'magnet', 'current_year', 'last_year']
        if parameter_value not in valid_filter_values:
            return Response(
                {'detail': f'Недопустимое значение фильтра: {parameter_value}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Валидация значений сортировки
    if parameter_type == 'sort':
        valid_sort_values = [
            'name_down',
            'name_up',
            'first_visit_date_down',
            'first_visit_date_up',
            'last_visit_date_down',
            'last_visit_date_up',
            'number_of_visits_down',
            'number_of_visits_up',
            'date_of_foundation_down',
            'date_of_foundation_up',
            'number_of_users_who_visit_city_down',
            'number_of_users_who_visit_city_up',
            'number_of_visits_all_users_down',
            'number_of_visits_all_users_up',
        ]
        if parameter_value not in valid_sort_values:
            return Response(
                {'detail': f'Недопустимое значение сортировки: {parameter_value}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    user = request.user
    user_id = user.id if isinstance(user, User) else None
    if user_id is None:
        raise drf_exc.PermissionDenied('User must be authenticated')

    # Сохранение или обновление настройки
    _, created = CityListDefaultSettings.objects.update_or_create(
        user_id=user_id,
        parameter_type=parameter_type,
        defaults={'parameter_value': parameter_value},
    )

    logger.info(
        request,
        f'(API: Save city list default settings) Settings {"created" if created else "updated"} '
        f'for user #{user_id}: {parameter_type}={parameter_value}',
    )

    return Response(
        {
            'status': 'success',
            'message': 'Настройки успешно сохранены',
            'created': created,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['DELETE'])
def delete_city_list_default_settings(request: Request) -> Response:
    """
    Удаляет настройки по умолчанию фильтрации или сортировки для списка городов.

    Принимает DELETE-параметры:
      - parameter_type (обязательный): 'filter' или 'sort'

    Возвращает статус успешного удаления или ошибку валидации.

    :param request: DRF Request с DELETE-параметрами
    :return: Response со статусом операции
    """
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Требуется аутентификация'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    parameter_type = request.data.get('parameter_type')

    if not parameter_type:
        return Response(
            {'detail': 'Параметр parameter_type является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if parameter_type not in ['filter', 'sort']:
        return Response(
            {'detail': 'parameter_type должен быть "filter" или "sort"'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user
    user_id = user.id if isinstance(user, User) else None
    if user_id is None:
        raise drf_exc.PermissionDenied('User must be authenticated')

    try:
        settings = CityListDefaultSettings.objects.get(
            user_id=user_id,
            parameter_type=parameter_type,
        )
        settings.delete()

        logger.info(
            request,
            f'(API: Delete city list default settings) Settings deleted '
            f'for user #{user_id}: {parameter_type}',
        )

        return Response(
            {
                'status': 'success',
                'message': 'Настройки успешно удалены',
            },
            status=status.HTTP_200_OK,
        )
    except CityListDefaultSettings.DoesNotExist:
        return Response(
            {
                'status': 'success',
                'message': 'Настройки не найдены',
            },
            status=status.HTTP_200_OK,
        )


@api_view(['GET'])
def get_visit_years(request: Request) -> Response:
    """
    Возвращает список всех уникальных годов, в которые пользователь посещал города.

    Принимает опциональный параметр:
    - country: код страны (ISO 3166-1 alpha-2) для фильтрации по стране

    Возвращает список годов в порядке убывания (от новых к старым).

    :param request: DRF Request
    :return: Response со списком годов
    """
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Пользователь должен быть авторизован'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user = request.user
    if not isinstance(user, User):
        return Response(
            {'detail': 'Не удалось определить пользователя'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_id = user.id

    # Получаем queryset посещённых городов с датами посещений
    queryset = VisitedCity.objects.filter(
        user_id=user_id,
        date_of_visit__isnull=False,
    ).select_related('city')

    # Фильтруем по стране, если указан параметр country
    country_code = request.GET.get('country')
    if country_code:
        print('\n\n\n', country_code, '\n\n\n')
        try:
            country = Country.objects.get(code=country_code)
            queryset = queryset.filter(city__country=country)
        except Country.DoesNotExist:
            return Response(
                {'detail': f'Страна с кодом {country_code} не найдена'},
                status=status.HTTP_404_NOT_FOUND,
            )

    # Извлекаем уникальные годы из дат посещений
    years = (
        queryset.annotate(year=ExtractYear('date_of_visit'))
        .values_list('year', flat=True)
        .distinct()
        .order_by('-year')
    )

    years_list = list(years)

    logger.info(
        request,
        f'(API) Successful request for visit years list (user #{user_id}, '
        f'country: {country_code or "all"}, years count: {len(years_list)})',
    )

    return Response({'years': years_list})
