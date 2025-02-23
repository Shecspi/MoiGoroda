"""
Реализует функции, взаимодействующие с моделью Region.
Любая работа с этой моделью должна происходить только через описанные в этом файле функции.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import (
    QuerySet,
    Count,
    Q,
    OuterRef,
    Avg,
    Exists,
    Subquery,
    IntegerField,
)
from django.http import HttpRequest

from city.models import City, VisitedCity
from region.models import Region
from services import logger


def get_all_visited_regions(user_id: int) -> QuerySet[Region]:
    """
    Получает из базы данных все посещённые регионы пользователя с ID, указанным в user_id.
    """
    return (
        Region.objects.select_related('area')
        .annotate(
            num_total=Count('city', distinct=True),
            num_visited=Count('city', filter=Q(city__visitedcity__user_id=user_id), distinct=True),
        )
        .order_by('-num_visited', 'title')
    )


def get_all_cities_in_region(
    request: HttpRequest,
    user: AbstractBaseUser,
    region_id: int,
    filter: str | None = None,
) -> QuerySet[City]:
    # Подзапрос для вычисления среднего рейтинга посещений города пользователем
    average_rating_subquery = (
        VisitedCity.objects.filter(city_id=OuterRef('pk'), user=user)
        .values('city_id')  # Группировка по городу
        .annotate(avg_rating=Avg('rating'))  # Вычисление среднего рейтинга
        .values('avg_rating')  # Передаем только рейтинг,
    )

    date_of_visit = VisitedCity.objects.filter(city_id=OuterRef('pk'), user=user)

    # Подзапрос для получения всех дат посещения города (нужно для фильтрации по годам)
    all_visit_dates = ArrayAgg(
        'visitedcity__date_of_visit',
        filter=Q(visitedcity__user=user),
        distinct=True,
    )

    # Посещён ли город?
    is_visited = Exists(VisitedCity.objects.filter(city_id=OuterRef('pk'), user=user))

    # Есть ли сувенир из города?
    has_magnet = Exists(
        VisitedCity.objects.filter(city_id=OuterRef('pk'), user=user, has_magnet=True)
    )

    # Подзапрос для вычисления количества посещений города
    visit_count = (
        VisitedCity.objects.filter(city_id=OuterRef('pk'), user=user)
        .values('city')
        .annotate(count=Count('id'))
        .values('count')
    )

    queryset = City.objects.filter(region_id=region_id).annotate(
        # Все даты посещения города (или только за указанный год).
        # Сортируются по возрастанию. Поэтому для получения первого посещения
        # в шаблоне можно использовать фильтр |first, а для последнего - |last.
        visit_dates=ArrayAgg(
            'visitedcity__date_of_visit',
            filter=Q(visitedcity__user=user),
            distinct=True,
            ordering='visitedcity__date_of_visit',
        ),
        # Посещён ли город. True или False
        is_visited=is_visited,
        # Имеется ли сувенир из города. True или False
        has_magnet=has_magnet,
    )

    if filter:
        try:
            queryset = apply_filter_to_queryset(queryset, user, filter)
        except KeyError:
            logger.warning(request, f"(Region) Unexpected value of the filter '{filter}'")

    queryset = (
        # Достаём все города региона, в том числе не посещённые
        queryset.annotate(
            visit_count=Subquery(
                visit_count,
                output_field=IntegerField(),
            ),
            visited_id=Subquery(
                VisitedCity.objects.filter(city_id=OuterRef('pk'), user=user).values('id')[:1],
                output_field=IntegerField(),
            ),
            rating=Subquery(
                average_rating_subquery,
                output_field=IntegerField(),
            ),
        ).values(
            'id',
            'title',
            'population',
            'date_of_foundation',
            'coordinate_width',
            'coordinate_longitude',
            'is_visited',
            'visit_count',
            'visited_id',
            'visit_dates',
            'has_magnet',
            'rating',
        )
    )

    return queryset


def apply_filter_to_queryset(
    queryset: QuerySet[City], user: AbstractBaseUser, filter: str
) -> QuerySet[City]:
    """
    Оставляет в queryset только значения, удовлетворяющие фильтру filter.

    На данный момент поддерживается 3 фильтра:
        - magnet - оставляет только города, из которых нет сувенира
        - current_year - оставляет только города, посещённые в текущем году
          (если есть хотя бы одна дата посещения в текущем году)
        - last_year - оставляет только города, посещённые в прошлом году
          (если есть хотя бы одна дата посещения в прошлом году)

    Фильтры current_year и last_year модифицируют поле visit_dates,
    оставляя в нём только даты посещения за указанный год.
    """
    current_year = datetime.today().year
    previous_year = current_year - 1

    match filter:
        case 'magnet':
            queryset = queryset.filter(has_magnet=False, is_visited=True)
        case 'current_year':
            queryset = queryset.annotate(
                visit_dates=ArrayAgg(
                    'visitedcity__date_of_visit',
                    filter=Q(visitedcity__user=user, visitedcity__date_of_visit__year=current_year),
                    distinct=True,
                    ordering='visitedcity__date_of_visit',
                ),
            ).exclude(Q(visit_dates=[]))
        case 'last_year':
            queryset = queryset.annotate(
                visit_dates=ArrayAgg(
                    'visitedcity__date_of_visit',
                    filter=Q(
                        visitedcity__user=user, visitedcity__date_of_visit__year=previous_year
                    ),
                    distinct=True,
                    ordering='visitedcity__date_of_visit',
                ),
            ).exclude(Q(visit_dates=[]))
        case _:
            raise KeyError

    return queryset
