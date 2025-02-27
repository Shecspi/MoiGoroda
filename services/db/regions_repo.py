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
    DateField,
    Value,
    Min,
    Max,
)
from django.db.models.functions import Coalesce

from city.models import City, VisitedCity
from region.models import Region


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
    user: AbstractBaseUser,
    region_id: int,
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
    # Здесь это считается на основе количества записей в VisitedCity, так как они могут быть без даты посещения.
    # А в фильтрах по годам считается на основе дат, так как посещение без даты не попадёт в этот фильтр.
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
        )
    )

    return queryset
