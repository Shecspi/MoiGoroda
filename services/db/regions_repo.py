"""
Реализует функции, взаимодействующие с моделью Region.
Любая работа с этой моделью должна происходить только через описанные в этом файле функции.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    QuerySet,
    Count,
    Q,
    OuterRef,
    Avg,
    Exists,
    Subquery,
    IntegerField,
    F,
    DateField,
    Value,
    Min,
    Max,
)
from django.db.models.functions import Coalesce
from django.http import HttpRequest

from city.models import City, VisitedCity
from region.models import Region
from services import logger
from services.db.selected_region.filter import apply_filter_to_queryset


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
    filter_name: str | None = None,
) -> QuerySet[City]:
    # Подзапрос для вычисления среднего рейтинга посещений города пользователем
    average_rating_subquery = (
        VisitedCity.objects.filter(city_id=OuterRef('pk'), user=user)
        .values('city_id')  # Группировка по городу
        .annotate(avg_rating=Avg('rating'))  # Вычисление среднего рейтинга
        .values('avg_rating')  # Передаем только рейтинг,
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
        visit_dates=Coalesce(
            ArrayAgg(
                'visitedcity__date_of_visit',
                filter=Q(visitedcity__user=user),
                ordering=['visitedcity__date_of_visit'],
            ),
            Value([], output_field=ArrayField(DateField())),
        ),
        first_visit_date=Min('visitedcity__date_of_visit', filter=Q(visitedcity__user=user)),
        last_visit_date=Max('visitedcity__date_of_visit', filter=Q(visitedcity__user=user)),
        # Количество посещений
        # Необходимо считать отдельно, так как может быть не указана дата посещения,
        # а, значит, просто посмотреть количество элементов в visit_dates не получится.
        number_of_visits=Subquery(
            visit_count,
            output_field=IntegerField(),
        ),
        # Посещён ли город. True или False
        is_visited=is_visited,
        # Имеется ли сувенир из города. True или False
        has_magnet=has_magnet,
    )

    if filter_name:
        try:
            queryset = apply_filter_to_queryset(queryset, user, filter_name)
        except KeyError:
            logger.warning(request, f"(Region) Unexpected value of the filter '{filter_name}'")

    queryset = (
        # Достаём все города региона, в том числе не посещённые
        queryset.annotate(
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
            'number_of_visits',
            'visited_id',
            'visit_dates',
            'first_visit_date',
            'last_visit_date',
            'has_magnet',
            'rating',
        )
    )

    return queryset


def apply_sort_to_queryset(queryset: QuerySet, sort_value: str) -> QuerySet:
    """
    Производит сортировку QuerySet на основе данных в 'sort_value'.

    @param queryset: QuerySet, который необходимо отсортировать.
    @param sort_value: Параметр, на основе которого происходит сортировка.
        Может принимать одно из 6 значений:
            - 'name_down' - по названию по возрастанию
            - 'name_up' - по названию по убыванию
            - 'date_down' - сначала недавно посещённые
            - 'date_up'. - сначала давно посещённые
            - 'default_auth' - по-умолчанию для авторизованного пользователя на странице "Города региона"
            - 'default_guest' - по-умолчанию для неавторизованного пользователя на странице "Города региона"
    @return: Отсортированный QuerySet или KeyError, если передан некорректный параметр `sort_value`.
    """
    match sort_value:
        case 'name_down':
            queryset = queryset.order_by('title')
        case 'name_up':
            queryset = queryset.order_by('-title')
        case 'date_down':
            queryset = queryset.order_by(
                '-is_visited', F('date_of_first_visit').asc(nulls_first=True)
            )
        case 'date_up':
            queryset = queryset.order_by(
                '-is_visited', F('date_of_first_visit').desc(nulls_last=True)
            )
        case 'default_auth':
            # queryset = queryset.order_by(
            #     '-is_visited', F('date_of_first_visit').desc(nulls_last=True), 'title'
            # )
            ...
        case 'default_guest':
            queryset = queryset.order_by('title')
        case _:
            raise KeyError

    return queryset
