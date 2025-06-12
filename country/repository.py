from django.db.models import QuerySet, OuterRef, Count, Subquery, IntegerField
from django.db.models.functions import Coalesce

from city.models import VisitedCity
from country.models import Country


def _get_countries_with_visited_city(
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


def get_countries_with_visited_city(user_id: int):
    """
    Возвращает перечень стран, в городах которых был пользователь `user_id`.
    Для каждой страны добавляются поля:
     - `total_cities` с количеством городов в этой стране
     - `visited_cities` с количеством посещённых городов.
    """
    queryset = VisitedCity.objects.filter(user_id=user_id, is_first_visit=True)
    return _get_countries_with_visited_city(queryset)


def get_countries_with_visited_city_in_year(user_id: int, year: int) -> QuerySet[Country]:
    """
    Возвращает перечень стран, в городах которых был пользователь `user_id` за год `year` (включая повторные посещения).
    Для каждой страны добавляются поля `total_cities` с количеством городов в этой стране и
    `visited_cities` с количеством посещённых городов.
    """
    queryset = VisitedCity.objects.filter(user_id=user_id, date_of_visit__year=year)
    return _get_countries_with_visited_city(queryset)


def get_countries_with_new_visited_city_in_year(user_id: int, year: int) -> QuerySet[Country]:
    """
    Возвращает перечень стран, в городах которых впервые был пользователь `user_id` за год `year`.
    Для каждой страны добавляются поля `total_cities` с количеством городов в этой стране и
    `visited_cities` с количеством посещённых городов.
    """
    queryset = VisitedCity.objects.filter(
        user_id=user_id, date_of_visit__year=year, is_first_visit=True
    )
    return _get_countries_with_visited_city(queryset)
