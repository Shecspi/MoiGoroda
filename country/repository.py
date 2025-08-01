from django.db.models import QuerySet, OuterRef, Count, Subquery, IntegerField, Value, Q
from django.db.models.functions import Coalesce

from city.models import VisitedCity
from country.models import Country
from region.models import Region


def _annotate_countries_with_visited_city_counts(
    queryset: QuerySet[VisitedCity],
) -> QuerySet[Country]:
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


def get_countries_with_visited_city(user_id: int) -> QuerySet[Country]:
    """
    Возвращает перечень стран, в городах которых был пользователь `user_id`.
    Для каждой страны добавляются поля:
     - `total_cities` с количеством городов в этой стране
     - `visited_cities` с количеством посещённых городов.
    """
    queryset = VisitedCity.objects.filter(user_id=user_id, is_first_visit=True)
    return _annotate_countries_with_visited_city_counts(queryset)


def get_countries_with_visited_city_in_year(user_id: int, year: int) -> QuerySet[Country]:
    """
    Возвращает перечень стран, в городах которых был пользователь `user_id` за год `year` (включая повторные посещения).
    Для каждой страны добавляются поля `total_cities` с количеством городов в этой стране и
    `visited_cities` с количеством посещённых городов.
    """
    queryset = VisitedCity.objects.filter(user_id=user_id, date_of_visit__year=year)
    return _annotate_countries_with_visited_city_counts(queryset)


def get_countries_with_new_visited_city_in_year(user_id: int, year: int) -> QuerySet[Country]:
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
) -> QuerySet[Country]:
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
