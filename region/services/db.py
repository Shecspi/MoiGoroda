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
    F,
    FloatField,
    ExpressionWrapper,
    Case,
    When,
)
from django.db.models.functions import Coalesce, Cast, Round

from city.models import City, VisitedCity
from region.models import Region, Area


def get_all_regions(country_id: int | None = None) -> QuerySet[Region]:
    """
    Возвращает QuerySet со всеми регионами и количеством городов в каждом из них.
    """
    queryset = Region.objects.all()

    if country_id:
        queryset = queryset.filter(country_id=country_id)

    return (
        queryset.select_related('area')
        .annotate(num_total=Count('city', distinct=True))
        .order_by('title')
    )


def get_number_of_regions(country_id: int | None) -> int:
    """
    Возвращает количество регионов, сохранённых в БД.
    Если указан параметр country_id, то возвращается количество регионов в конкретной стране.
    """
    queryset = Region.objects.all()
    if country_id:
        queryset = queryset.filter(country_id=country_id)
    return queryset.count()


def get_all_region_with_visited_cities(
    user_id: int, country_id: int | None = None
) -> QuerySet[Region]:
    """
    Возвращает QuerySet со всеми регионами, количеством городов в каждом из них и
    количеством посещённых городов пользователем с ID равным user_id.
    """
    queryset = Region.objects.all()

    if country_id:
        queryset = queryset.filter(country_id=country_id)

    return (
        queryset.select_related('area')
        .annotate(
            num_total=Count('city', distinct=True),
            num_visited=Count('city', filter=Q(city__visitedcity__user_id=user_id), distinct=True),
        )
        .annotate(
            ratio_visited=Round(
                ExpressionWrapper(
                    Case(
                        When(num_total=0, then=Value(0.0)),
                        default=100 * F('num_visited') / F('num_total'),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField(),
                )
            ),
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

    queryset = City.objects.filter(region_id=region_id).annotate(
        # Все даты посещения города (или только за указанный год).
        # Сортируются по возрастанию. Поэтому для получения первого посещения
        # в шаблоне можно использовать фильтр |first, а для последнего - |last.
        visit_dates=Coalesce(
            ArrayAgg(
                'visitedcity__date_of_visit',
                filter=Q(visitedcity__user=user) & ~Q(visitedcity__date_of_visit=None),
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
        number_of_users_who_visit_city=Subquery(
            number_of_users_who_visit_city, output_field=IntegerField()
        ),
        number_of_visits_all_users=Subquery(number_of_visits_all_users),
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


def get_number_of_visited_regions(user_id: int, country_id: int | None = None) -> int:
    """
    Возвращает количество посещённых регионов пользователя с ID user_id.
    """
    if country_id:
        queryset = get_all_region_with_visited_cities(user_id, country_id)
    else:
        queryset = get_all_region_with_visited_cities(user_id)
    return queryset.filter(num_visited__gt=0).count()


def get_number_of_finished_regions(user_id: int, country_id: int | None = None) -> int:
    """
    Возвращает количество регионов, в которых пользователь с ID == user_id посетил все города.
    Эта функция расширяет функцию get_all_visited_regions(), добавляя одно условие фильтрации.
    """
    if country_id:
        queryset = get_all_region_with_visited_cities(user_id, country_id)
    else:
        queryset = get_all_region_with_visited_cities(user_id)
    return queryset.filter(num_total=F('num_visited')).count()


def get_visited_areas(user_id: int) -> QuerySet:
    """
    Возвращает последовательность федеральных округов из БД, которая имеет дополнительные поля:
     - total_regions: количество регионов в федеральном округе;
     - visited_regions: количество посещённых регионов в федеральном округе;
     - ratio_visited: процентное соотношение количества посещённых регионов к общему количеству.

     Записи сортируются сначала по полю ratio_visited (от большего к меньшему), а потом по полю title.
    """
    return (
        Area.objects.all()
        .annotate(
            # Добавляем в QuerySet общее количество регионов в округе
            total_regions=Count('region', distinct=True),
            # Добавляем в QuerySet количество посещённых регионов в округе
            visited_regions=Count(
                'region', filter=Q(region__visitedcity__user__id=user_id), distinct=True
            ),
            # Добавляем в QuerySet процентное соотношение посещённых регионов.
            # Без Cast(..., output_field=...) деление F() на F() выдаёт int, то есть очень сильно теряется точность.
            # Например, 76 / 54 получается 1.
            ratio_visited=(
                Cast(F('visited_regions'), output_field=FloatField())
                / Cast(F('total_regions'), output_field=FloatField())
            )
            * 100,
        )
        .order_by('-ratio_visited', 'title')
    )


def get_number_all_areas() -> int:
    return Area.objects.count()


def get_number_visited_areas(user_id: int) -> int:
    return get_visited_areas(user_id).filter(visited_regions__gt=0).count()
