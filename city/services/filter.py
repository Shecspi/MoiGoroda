from datetime import date
from typing import Callable

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import (
    QuerySet,
    Q,
    Min,
    Max,
    Subquery,
    OuterRef,
    DateField,
    Count,
    IntegerField,
)
from typing import NoReturn

from city.models import VisitedCity


def apply_filter_to_queryset(
    queryset: QuerySet[VisitedCity], user_id: int, filter_name: str
) -> QuerySet[VisitedCity] | NoReturn:
    func = FILTER_FUNCTIONS.get(filter_name)
    if not func:
        raise KeyError(f'Неизвестный фильтр: {filter_name}')

    return func(queryset, user_id)


def filter_has_magnet(queryset: QuerySet[VisitedCity], user_id: int) -> QuerySet[VisitedCity]:
    """
    Фильтр оставляет только посещённые города, из которых имеется сувенир.
    В модели VisitedCity поле, содержащее информацию о сувенире, называется 'has_magnet',
    но в итоговом QuerySet оно меняется на 'has_souvenir'
    (которое является обобщённым для всех одинаковых посещённых городов),
    поэтому именно по нему происходит фильтрация.
    """
    return queryset.filter(has_souvenir=True)  # type: ignore[misc]


def filter_has_no_magnet(queryset: QuerySet[VisitedCity], user_id: int) -> QuerySet[VisitedCity]:
    """
    Фильтр оставляет только посещённые города, из которых нет сувенира.
    В модели VisitedCity поле, содержащее информацию о сувенире, называется 'has_magnet',
    но в итоговом QuerySet оно меняется на 'has_souvenir'
    (которое является обобщённым для всех одинаковых посещённых городов),
    поэтому именно по нему происходит фильтрация.
    """
    return queryset.filter(has_souvenir=False)  # type: ignore[misc]


def filter_current_year(queryset: QuerySet[VisitedCity], user_id: int) -> QuerySet[VisitedCity]:
    return filter_by_year(queryset, user_id, date.today().year)


def filter_last_year(queryset: QuerySet[VisitedCity], user_id: int) -> QuerySet[VisitedCity]:
    return filter_by_year(queryset, user_id, date.today().year - 1)


def filter_by_year(
    queryset: QuerySet[VisitedCity], user_id: int, year: int
) -> QuerySet[VisitedCity]:
    """
    Фильтр оставляет только города, посещённые в указанном году.
    В поле visit_dates отображаются только даты посещений в указанном году.
    Аналогично с полями first_visit_date и last_visit_date.
    В поле number_of_visits хранится количество посещений города в указанном году.
    """
    visit_dates_subquery = (
        VisitedCity.objects.filter(user_id=user_id, city_id=OuterRef('city_id'))
        .values('city_id')
        .annotate(
            visit_dates=ArrayAgg(
                'date_of_visit',
                filter=Q(date_of_visit__year=year),
                distinct=True,
                ordering='date_of_visit',
            )
        )
        .values('visit_dates')
    )

    first_visit_dates_subquery = (
        VisitedCity.objects.filter(
            user_id=user_id,
            city_id=OuterRef('city_id'),
            date_of_visit__year=year,
        )
        .values('city_id')
        .annotate(first_date=Min('date_of_visit'))
        .values('first_date')
    )

    last_visit_dates_subquery = (
        VisitedCity.objects.filter(
            user_id=user_id,
            city_id=OuterRef('city_id'),
            date_of_visit__year=year,
        )
        .values('city_id')
        .annotate(last_date=Max('date_of_visit'))  # Максимальная дата
        .values('last_date')
    )

    number_of_visits_subquery = (
        VisitedCity.objects.filter(
            user_id=user_id, city_id=OuterRef('city_id'), date_of_visit__year=year
        )
        .values('city_id')
        .annotate(count=Count('id'))
        .values('count')
    )

    return (
        queryset.annotate(
            visit_dates=Subquery(visit_dates_subquery),
            first_visit_date=Subquery(
                first_visit_dates_subquery,
                output_field=DateField(),
            ),
            last_visit_date=Subquery(
                last_visit_dates_subquery,
                output_field=DateField(),
            ),
        )
        .exclude(Q(visit_dates=[]))
        .annotate(
            number_of_visits=Subquery(
                number_of_visits_subquery,
                output_field=IntegerField(),
            )
        )
    )


FILTER_FUNCTIONS: dict[str, Callable[[QuerySet[VisitedCity], int], QuerySet[VisitedCity]]] = {
    'magnet': filter_has_magnet,
    'no_magnet': filter_has_no_magnet,
    'current_year': filter_current_year,
    'last_year': filter_last_year,
}
