"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json
import uuid
from typing import Any

from django.contrib.auth.models import User
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (
    Avg,
    Count,
    Exists,
    IntegerField,
    Max,
    Min,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Value,
)
from django.db.models.functions import Round
from django.http import Http404
from django.utils.safestring import mark_safe

from city.models import City, VisitedCity
from collection.filter import apply_filter_to_queryset
from collection.models import Collection, PersonalCollection
from collection.repository import CollectionRepository
from services import logger
from utils.CollectionListMixin import CollectionListMixin


class CollectionListService:
    """
    Сервис для бизнес-логики работы со списком коллекций.
    """

    def __init__(self, repository: CollectionRepository | None = None):
        self.repository = repository or CollectionRepository()
        self.mixin = CollectionListMixin()

    def get_collections(
        self,
        user: User | None,
        filter_value: str | None = None,
        sort_value: str | None = None,
        request: Any = None,
    ) -> tuple[QuerySet[Collection, Any], dict[str, Any]]:
        """
        Получает коллекции с применением фильтров и сортировки.

        :param user: Пользователь, для которого нужно получить коллекции.
        :param filter_value: Значение фильтра (например, 'not_started', 'finished').
        :param sort_value: Значение сортировки (например, 'name_down', 'progress_up').
        :param request: HTTP request для логирования (опционально).
        :return: Кортеж из QuerySet коллекций и словаря со статистикой.
        """
        # Получаем коллекции с аннотациями
        queryset = self.repository.get_collections_with_annotations(user)

        # Получаем список посещённых городов для пользователя
        visited_cities = None
        if user and user.is_authenticated:
            visited_cities = self.repository.get_visited_city_ids(user)

        # Подсчитываем статистику
        qty_of_collections = queryset.count()
        qty_of_started_collections = 0
        qty_of_finished_collections = 0

        if user and user.is_authenticated:
            for collection in queryset:
                if collection.qty_of_visited_cities > 0:
                    qty_of_started_collections += 1
                if collection.qty_of_visited_cities == collection.qty_of_cities:
                    qty_of_finished_collections += 1

        # Применяем фильтр
        filter_param = filter_value if filter_value else ''
        if filter_param:
            try:
                queryset = self.mixin.apply_filter_to_queryset(queryset, filter_param)
            except KeyError:
                filter_param = ''
                if request:
                    logger.warning(
                        request,
                        f"(Collections) Unexpected value of the filter '{filter_value}'",
                    )

        # Применяем сортировку
        if user and user.is_authenticated:
            sort_param = sort_value if sort_value else 'default_auth'
        else:
            sort_param = sort_value if sort_value else 'default_guest'

        try:
            queryset = self.mixin.apply_sort_to_queryset(queryset, sort_param)
        except KeyError:
            if request:
                logger.warning(
                    request, f"(Collections) Unexpected value of the sort '{sort_value}'"
                )
            sort_param = 'default_auth' if user and user.is_authenticated else 'default_guest'
            queryset = self.mixin.apply_sort_to_queryset(queryset, sort_param)

        statistics = {
            'qty_of_collections': qty_of_collections,
            'qty_of_started_collections': qty_of_started_collections,
            'qty_of_finished_collections': qty_of_finished_collections,
            'visited_cities': visited_cities,
            'filter': filter_param,
            'sort': sort_param,
        }

        return queryset, statistics

    def get_personal_collections(self, user: User) -> QuerySet[PersonalCollection, Any]:
        """
        Получает персональные коллекции пользователя.

        :param user: Пользователь, чьи персональные коллекции нужно получить.
        :return: QuerySet персональных коллекций с аннотациями.
        """
        return self.repository.get_personal_collections_with_annotations(user)

    def get_context_data(
        self,
        user: User | None,
        sort: str,
        filter_param: str,
        qty_of_collections: int,
        qty_of_started_collections: int,
        qty_of_finished_collections: int,
    ) -> dict[str, Any]:
        """
        Формирует контекст для шаблона списка коллекций.

        :param user: Пользователь.
        :param sort: Параметр сортировки.
        :param filter_param: Параметр фильтрации.
        :param qty_of_collections: Общее количество коллекций.
        :param qty_of_started_collections: Количество начатых коллекций.
        :param qty_of_finished_collections: Количество завершённых коллекций.
        :return: Словарь с данными для контекста шаблона.
        """
        context: dict[str, Any] = {
            'sort': sort,
            'filter': filter_param,
            'qty_of_collections': qty_of_collections,
            'qty_of_started_colelctions': qty_of_started_collections,
            'qty_of_finished_colelctions': qty_of_finished_collections,
            'active_page': 'collection',
            'page_title': 'Коллекции городов',
            'page_description': (
                'Города России, распределённые по различным коллекциям. Путешествуйте по России и закрывайте коллекции.'
            ),
        }

        # Получаем персональные коллекции
        if user and user.is_authenticated:
            context['personal_collections'] = self.get_personal_collections(user)
        else:
            context['personal_collections'] = PersonalCollection.objects.none()

        # Формируем URL параметры для сортировки и фильтрации
        url_params_for_sort = '' if sort == 'default_auth' or sort == 'default_guest' else sort

        context['url_for_filter_not_started'] = self.mixin.get_url_params(
            'not_started' if filter_param != 'not_started' else '',
            url_params_for_sort,
        )
        context['url_for_filter_finished'] = self.mixin.get_url_params(
            'finished' if filter_param != 'finished' else '', url_params_for_sort
        )
        context['url_for_sort_name_down'] = self.mixin.get_url_params(filter_param, 'name_down')
        context['url_for_sort_name_up'] = self.mixin.get_url_params(filter_param, 'name_up')
        context['url_for_sort_progress_down'] = self.mixin.get_url_params(
            filter_param, 'progress_down'
        )
        context['url_for_sort_progress_up'] = self.mixin.get_url_params(filter_param, 'progress_up')

        return context


class PersonalCollectionService:
    """
    Сервис для бизнес-логики работы с персональными коллекциями.
    """

    def __init__(self, repository: CollectionRepository | None = None):
        self.repository = repository or CollectionRepository()

    def get_collection_with_access_check(
        self, collection_id: uuid.UUID, user: Any
    ) -> PersonalCollection:
        """
        Получает персональную коллекцию с проверкой доступа.

        :param collection_id: UUID персональной коллекции.
        :param user: Пользователь, запрашивающий доступ.
        :return: Объект PersonalCollection.
        :raises Http404: Если коллекция не найдена или доступ запрещён.
        """
        try:
            collection = self.repository.get_personal_collection_by_id(collection_id)
        except ObjectDoesNotExist:
            # Логирование ошибки доступа (request не доступен в сервисе)
            raise Http404

        # Коллекция доступна, если:
        # 1. Она публичная (is_public = True) - доступна всем, даже неавторизованным
        # 2. ИЛИ пользователь авторизован И является владельцем коллекции
        if not collection.is_public:
            if not user.is_authenticated or collection.user != user:
                raise Http404

        return collection

    def get_cities_for_collection(
        self, collection_id: uuid.UUID, collection_owner: User, filter_value: str | None = None
    ) -> tuple[Any, dict[str, Any]]:
        """
        Получает города персональной коллекции с применением фильтров.

        :param collection_id: UUID персональной коллекции.
        :param collection_owner: Владелец коллекции (для определения посещённых городов).
        :param filter_value: Значение фильтра (например, 'visited', 'not_visited').
        :return: Кортеж из QuerySet городов и словаря со статистикой.
        """
        cities = get_all_cities_from_personal_collection(collection_id, collection_owner)

        qty_of_visited_cities = sum(1 for city in cities if getattr(city, 'is_visited', False))
        qty_of_cities = len(cities)

        # Применяем фильтр
        filter_param = filter_value if filter_value else ''
        if filter_param:
            try:
                cities = apply_filter_to_queryset(cities, filter_param)
            except KeyError:
                filter_param = ''
                # Логирование ошибки фильтра (request не доступен в сервисе)

        statistics = {
            'qty_of_cities': qty_of_cities,
            'qty_of_visited_cities': qty_of_visited_cities,
            'filter': filter_param,
        }

        return cities, statistics

    def get_list_context_data(
        self,
        collection: PersonalCollection,
        cities: Any,
        qty_of_cities: int,
        qty_of_visited_cities: int,
        filter_param: str,
    ) -> dict[str, Any]:
        """
        Формирует контекст для шаблона списка городов персональной коллекции.

        :param collection: Объект PersonalCollection.
        :param cities: QuerySet городов.
        :param qty_of_cities: Общее количество городов.
        :param qty_of_visited_cities: Количество посещённых городов.
        :param filter_param: Параметр фильтрации.
        :return: Словарь с данными для контекста шаблона.
        """
        # Для списка передаём упрощённые данные
        cities_data = [
            {
                'name': city.title,
                'lat': float(str(city.coordinate_width).replace(',', '.')),
                'lon': float(str(city.coordinate_longitude).replace(',', '.')),
                'is_visited': city.is_visited,
            }
            for city in cities
        ]

        return {
            'cities': mark_safe(json.dumps(cities_data)),
            'filter': filter_param,
            'qty_of_cities': qty_of_cities,
            'qty_of_visited_cities': qty_of_visited_cities,
            'pk': collection.id,
            'page_title': collection.title,
            'collection': collection,
            'page_description': f'Города в персональной коллекции "{collection.title}".',
        }

    def get_map_context_data(
        self,
        collection: PersonalCollection,
        cities: Any,
        qty_of_cities: int,
        qty_of_visited_cities: int,
    ) -> dict[str, Any]:
        """
        Формирует контекст для шаблона карты городов персональной коллекции.

        :param collection: Объект PersonalCollection.
        :param cities: QuerySet городов.
        :param qty_of_cities: Общее количество городов.
        :param qty_of_visited_cities: Количество посещённых городов.
        :return: Словарь с данными для контекста шаблона.
        """
        from django.conf import settings

        return {
            'all_cities': cities,
            'qty_of_cities': qty_of_cities,
            'qty_of_visited_cities': qty_of_visited_cities,
            'TILE_LAYER': getattr(
                settings, 'TILE_LAYER', 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
            ),
            'pk': collection.id,
            'page_title': collection.title,
            'collection': collection,
            'page_description': f'Карта городов в персональной коллекции "{collection.title}".',
        }


def get_all_cities_from_collection(
    collection_id: int, user: User | None = None
) -> QuerySet[City, City]:
    """
    Возвращает все города в коллекции с ID = collection_id.
    Если указан user, то возвращаемый QuerySet аннотируется дополнительными полями.
    """
    cities_id = [city.id for city in Collection.objects.get(id=collection_id).city.all()]

    if user:
        base_qs = VisitedCity.objects.filter(user=user, city=OuterRef('pk'))

        # Подзапрос для сбора всех дат посещений города
        visit_dates_subquery = (
            base_qs.values('city')
            .annotate(
                visit_dates=ArrayAgg('date_of_visit', distinct=False, filter=~Q(date_of_visit=None))
            )
            .values('visit_dates')
        )

        # Подзапрос для даты первого посещения (first_visit_date)
        first_visit_date_subquery = (
            base_qs.values('city')
            .annotate(first_visit_date=Min('date_of_visit'))
            .values('first_visit_date')
        )

        # Подзапрос для даты последнего посещения (first_visit_date)
        last_visit_date_subquery = (
            base_qs.values('city')
            .annotate(last_visit_date=Max('date_of_visit'))
            .values('last_visit_date')
        )

        # Подзапрос для вычисления среднего рейтинга посещений города пользователем
        average_rating_subquery = (
            base_qs.values('city_id')  # Группировка по городу
            .annotate(avg_rating=Avg('rating'))  # Вычисление среднего рейтинга
            .values('avg_rating')  # Передаем только рейтинг
        )

        # Есть ли сувенир из города?
        has_souvenir = Exists(base_qs.filter(has_magnet=True))

        # Подзапрос для количества посещений города пользователем
        city_visits_subquery = (
            base_qs.values('city_id')  # Группировка по городу
            .annotate(count=Count('*'))  # Подсчет записей (число посещений)
            .values('count')  # Передаем только поле count
        )

        # Подзапрос для получения количество пользователей, посетивших город
        number_of_users_who_visit_city = (
            VisitedCity.objects.filter(city=OuterRef('pk'), is_first_visit=True)
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        # Подзапрос для получения общего количества посещений города
        number_of_visits_all_users = (
            VisitedCity.objects.filter(city=OuterRef('pk'))
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        return (
            City.objects.filter(id__in=cities_id)
            .select_related('region', 'country')
            .annotate(
                is_visited=Exists(VisitedCity.objects.filter(city_id=OuterRef('pk'), user=user)),
                visit_dates=Subquery(visit_dates_subquery),
                first_visit_date=Subquery(first_visit_date_subquery),
                last_visit_date=Subquery(last_visit_date_subquery),
                average_rating=(
                    Round((Subquery(average_rating_subquery) * 2), 0) / 2
                ),  # Округление до 0.5
                has_souvenir=has_souvenir,
                number_of_visits=Subquery(city_visits_subquery, output_field=IntegerField()),
                number_of_users_who_visit_city=Subquery(
                    number_of_users_who_visit_city, output_field=IntegerField()
                ),
                number_of_visits_all_users=Subquery(number_of_visits_all_users),
            )
        )
    else:
        # Подзапрос для получения количество пользователей, посетивших город
        number_of_users_who_visit_city = (
            VisitedCity.objects.filter(city=OuterRef('pk'), is_first_visit=True)
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        # Подзапрос для получения общего количества посещений города
        number_of_visits_all_users = (
            VisitedCity.objects.filter(city=OuterRef('pk'))
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        return (
            City.objects.filter(id__in=cities_id)
            .select_related('region', 'country')
            .annotate(
                is_visited=Value(False),
                number_of_users_who_visit_city=Subquery(
                    number_of_users_who_visit_city, output_field=IntegerField()
                ),
                number_of_visits_all_users=Subquery(number_of_visits_all_users),
            )
        )


def get_all_cities_from_personal_collection(
    collection_id: uuid.UUID, user: User | None = None
) -> QuerySet[City, City]:
    """
    Возвращает все города в персональной коллекции с ID = collection_id.
    Если указан user, то возвращаемый QuerySet аннотируется дополнительными полями.
    """
    cities_id = [city.id for city in PersonalCollection.objects.get(id=collection_id).city.all()]

    if user:
        base_qs = VisitedCity.objects.filter(user=user, city=OuterRef('pk'))

        # Подзапрос для сбора всех дат посещений города
        visit_dates_subquery = (
            base_qs.values('city')
            .annotate(
                visit_dates=ArrayAgg('date_of_visit', distinct=False, filter=~Q(date_of_visit=None))
            )
            .values('visit_dates')
        )

        # Подзапрос для даты первого посещения (first_visit_date)
        first_visit_date_subquery = (
            base_qs.values('city')
            .annotate(first_visit_date=Min('date_of_visit'))
            .values('first_visit_date')
        )

        # Подзапрос для даты последнего посещения (first_visit_date)
        last_visit_date_subquery = (
            base_qs.values('city')
            .annotate(last_visit_date=Max('date_of_visit'))
            .values('last_visit_date')
        )

        # Подзапрос для вычисления среднего рейтинга посещений города пользователем
        average_rating_subquery = (
            base_qs.values('city_id')  # Группировка по городу
            .annotate(avg_rating=Avg('rating'))  # Вычисление среднего рейтинга
            .values('avg_rating')  # Передаем только рейтинг
        )

        # Есть ли сувенир из города?
        has_souvenir = Exists(base_qs.filter(has_magnet=True))

        # Подзапрос для количества посещений города пользователем
        city_visits_subquery = (
            base_qs.values('city_id')  # Группировка по городу
            .annotate(count=Count('*'))  # Подсчет записей (число посещений)
            .values('count')  # Передаем только поле count
        )

        # Подзапрос для получения количество пользователей, посетивших город
        number_of_users_who_visit_city = (
            VisitedCity.objects.filter(city=OuterRef('pk'), is_first_visit=True)
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        # Подзапрос для получения общего количества посещений города
        number_of_visits_all_users = (
            VisitedCity.objects.filter(city=OuterRef('pk'))
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        return (
            City.objects.filter(id__in=cities_id)
            .select_related('region', 'country')
            .annotate(
                is_visited=Exists(VisitedCity.objects.filter(city_id=OuterRef('pk'), user=user)),
                visit_dates=Subquery(visit_dates_subquery),
                first_visit_date=Subquery(first_visit_date_subquery),
                last_visit_date=Subquery(last_visit_date_subquery),
                average_rating=(
                    Round((Subquery(average_rating_subquery) * 2), 0) / 2
                ),  # Округление до 0.5
                has_souvenir=has_souvenir,
                number_of_visits=Subquery(city_visits_subquery, output_field=IntegerField()),
                number_of_users_who_visit_city=Subquery(
                    number_of_users_who_visit_city, output_field=IntegerField()
                ),
                number_of_visits_all_users=Subquery(number_of_visits_all_users),
            )
        )
    else:
        # Подзапрос для получения количество пользователей, посетивших город
        number_of_users_who_visit_city = (
            VisitedCity.objects.filter(city=OuterRef('pk'), is_first_visit=True)
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        # Подзапрос для получения общего количества посещений города
        number_of_visits_all_users = (
            VisitedCity.objects.filter(city=OuterRef('pk'))
            .values('city')
            .annotate(count=Count('*'))
            .values('count')[:1]
        )

        return (
            City.objects.filter(id__in=cities_id)
            .select_related('region', 'country')
            .annotate(
                is_visited=Value(False),
                number_of_users_who_visit_city=Subquery(
                    number_of_users_who_visit_city, output_field=IntegerField()
                ),
                number_of_visits_all_users=Subquery(number_of_visits_all_users),
            )
        )
