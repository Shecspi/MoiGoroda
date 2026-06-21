# ----------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Репозиторные функции для стран и агрегатов по посещённым городам/регионам."""

from django.db import connection
from django.db.models import Count, IntegerField, OuterRef, Q, QuerySet, Subquery, Value
from django.db.models.functions import Coalesce

from city.models import City, VisitedCity
from country.dto import CountryVisitedCityCounts
from country.models import Country
from region.models import Region


def _annotate_countries_with_visited_city_counts(
    queryset: QuerySet[VisitedCity, VisitedCity],
) -> QuerySet[Country, Country]:
    """
    Аннотирует подзапрос `queryset` двумя дополнительными полями:
     - `total_cities` с количеством городов в этой стране;
     - `visited_cities` с количеством посещённых городов.
    """
    visited_counts_subquery = (
        queryset.filter(city__country=OuterRef('pk'))
        .values('city__country')
        .annotate(unique_city_count=Count('city'))
        .values('unique_city_count')[:1]
    )

    return (
        Country.objects.annotate(
            total_cities=Count('city', distinct=True),
            visited_cities=Coalesce(
                Subquery(visited_counts_subquery, output_field=IntegerField()), 0
            ),
        )
        .filter(visited_cities__gt=0)
        .order_by('-visited_cities')
    )


def get_countries_with_visited_city(user_id: int) -> QuerySet[Country, Country]:
    """
    Возвращает перечень стран, в городах которых был пользователь `user_id`.
    Для каждой страны добавляются поля:
     - `total_cities` с количеством городов в этой стране
     - `visited_cities` с количеством посещённых городов.
    """
    queryset = VisitedCity.objects.filter(user_id=user_id, is_first_visit=True)
    return _annotate_countries_with_visited_city_counts(queryset)


def get_countries_visited_city_counts(user_id: int) -> list[CountryVisitedCityCounts]:
    """
    Возвращает страны, где пользователь посещал города, с количеством посещённых
    и общим количеством городов в каждой стране. Учитываются только города с is_first_visit.

    Метод используется в статистическом endpoint и намеренно выполняет два узких агрегата:
    отдельно по посещениям пользователя и отдельно по городам найденных стран. Это быстрее
    старого запроса с аннотацией всех стран и correlated subquery.
    """
    visited_rows = list(
        VisitedCity.objects.filter(user_id=user_id, is_first_visit=True)
        .values('city__country_id', 'city__country__name')
        .annotate(visited_cities=Count('city_id'))
        .order_by('-visited_cities', 'city__country_id')
    )
    country_ids = [row['city__country_id'] for row in visited_rows]
    total_cities_by_country = dict(
        City.objects.filter(country_id__in=country_ids)
        .values('country_id')
        .annotate(total_cities=Count('id'))
        .values_list('country_id', 'total_cities')
    )

    return [
        CountryVisitedCityCounts(
            pk=int(row['city__country_id']),
            name=str(row['city__country__name']),
            visited_cities=int(row['visited_cities']),
            total_cities=int(total_cities_by_country.get(row['city__country_id'], 0)),
        )
        for row in visited_rows
    ]


def get_unique_visited_cities_country_ranks(
    country_visit_counts: dict[int, int],
) -> dict[int, int]:
    """
    Возвращает рейтинги пользователя по количеству уникально посещённых городов
    для переданных стран.

    На вход передаётся словарь `{country_id: visited_cities}` для одного пользователя.
    Rank считается как количество пользователей, посетивших в этой стране больше городов,
    плюс один. Это повторяет прежнюю формулу endpoint, но делает один bulk-запрос вместо
    отдельного запроса на каждую страну.
    """
    if not country_visit_counts:
        return {}

    users_with_more_by_country = dict.fromkeys(country_visit_counts.keys(), 0)
    threshold_values_sql = ', '.join(['(%s, %s)'] * len(country_visit_counts))
    query_params: list[int | bool] = []
    for country_id, visited_cities in country_visit_counts.items():
        query_params.extend([country_id, visited_cities])
    query_params.append(True)

    visited_city_table = connection.ops.quote_name(VisitedCity._meta.db_table)
    city_table = connection.ops.quote_name(City._meta.db_table)

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            WITH thresholds(country_id, visited_cities) AS (
                VALUES {threshold_values_sql}
            ),
            user_country_counts AS (
                SELECT
                    city.country_id,
                    visited_city.user_id,
                    COUNT(DISTINCT visited_city.city_id) AS unique_visited_cities
                FROM {visited_city_table} AS visited_city
                INNER JOIN {city_table} AS city ON city.id = visited_city.city_id
                INNER JOIN thresholds ON thresholds.country_id = city.country_id
                WHERE visited_city.is_first_visit = %s
                GROUP BY city.country_id, visited_city.user_id
            )
            SELECT
                user_country_counts.country_id,
                COUNT(*) AS users_with_more
            FROM user_country_counts
            INNER JOIN thresholds ON thresholds.country_id = user_country_counts.country_id
            WHERE user_country_counts.unique_visited_cities > thresholds.visited_cities
            GROUP BY user_country_counts.country_id
            """,
            query_params,
        )
        for country_id, users_with_more in cursor.fetchall():
            users_with_more_by_country[int(country_id)] = int(users_with_more)

    return {
        country_id: users_with_more + 1
        for country_id, users_with_more in users_with_more_by_country.items()
    }


def get_countries_with_visited_city_in_year(user_id: int, year: int) -> QuerySet[Country, Country]:
    """
    Возвращает перечень стран, в городах которых был пользователь `user_id` за год `year` (включая повторные посещения).
    Для каждой страны добавляются поля `total_cities` с количеством городов в этой стране и
    `visited_cities` с количеством посещённых городов.
    """
    queryset = VisitedCity.objects.filter(user_id=user_id, date_of_visit__year=year)
    return _annotate_countries_with_visited_city_counts(queryset)


def get_countries_with_new_visited_city_in_year(
    user_id: int, year: int
) -> QuerySet[Country, Country]:
    """
    Возвращает перечень стран, в городах которых впервые был пользователь `user_id` за год `year`.
    Для каждой страны добавляются поля `total_cities` с количеством городов в этой стране и
    `visited_cities` с количеством посещённых городов.
    """
    queryset = VisitedCity.objects.filter(
        user_id=user_id, date_of_visit__year=year, is_first_visit=True
    )
    return _annotate_countries_with_visited_city_counts(queryset)


def get_list_of_countries_with_visited_regions(
    user_id: int, year: int | None = None
) -> QuerySet[Country, Country]:
    # Подзапрос для количества всех регионов в стране
    regions_in_country = (
        Region.objects.filter(country=OuterRef('pk'))
        .values('country')
        .annotate(count=Count('pk', distinct=True))
        .values('count')[:1]
    )

    # Подзапрос для количества посещённых пользователем регионов в каждой стране
    if year:
        subquery_filter_condition = (
            Q(country=OuterRef('pk'))
            & Q(city__visitedcity__user_id=user_id)
            & Q(city__visitedcity__date_of_visit__year=year)
        )
    else:
        subquery_filter_condition = Q(country=OuterRef('pk')) & Q(
            city__visitedcity__user_id=user_id
        )
    visited_regions_in_country = (
        Region.objects.filter(subquery_filter_condition)
        .values('country')  # группируем по стране
        .annotate(count=Count('pk', distinct=True))  # считаем уникальные регионы
        .values('count')[:1]
    )

    return (
        Country.objects.filter(city__visitedcity__user_id=user_id)
        .distinct()
        .annotate(
            number_of_regions=Coalesce(
                Subquery(regions_in_country, output_field=IntegerField()), Value(0)
            ),
            number_of_visited_regions=Coalesce(
                Subquery(visited_regions_in_country, output_field=IntegerField()), Value(0)
            ),
        )
        .filter(number_of_visited_regions__gt=0)
        .order_by('-number_of_visited_regions')
    )
