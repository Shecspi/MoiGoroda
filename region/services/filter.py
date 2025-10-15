"""
Модуль фильтрации городов региона.

Этот файл содержит функции для фильтрации списка городов региона по различным критериям,
таким как наличие/отсутствие сувенира и даты посещения.
Функции позволяют динамически изменять QuerySet в зависимости от выбранного фильтра.

Основные фильтры:
- has_magnet: оставляет только города, из которых имеется сувенира.
- has_no_magnet: оставляет только города, из которых нет сувенира.
- current_year: оставляет только города, посещённые в текущем году.
- last_year: оставляет только города, посещённые в прошлом году.

Фильтры current_year и last_year обновляют информацию о датах посещений и их количестве.

Добавление нового фильтра:
1. Создайте новую функцию фильтрации в том же формате, что и существующие (`filter_<название>`).
2. Внутри функции изменяйте QuerySet в соответствии с необходимыми критериями.
3. Добавьте функцию в словарь `FILTER_FUNCTIONS`, используя строковый ключ для её вызова.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""
# mypy: disable-error-code="misc"

from datetime import datetime
from typing import Callable, NoReturn

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import (
    QuerySet,
    Q,
    Min,
    Max,
    Func,
    IntegerField,
)

from city.models import City


class ArrayLength(Func):
    """Функция для подсчёта количества элементов в массиве PostgreSQL"""

    function = 'CARDINALITY'
    output_field = IntegerField()


def apply_filter_to_queryset(
    queryset: QuerySet[City], user: AbstractBaseUser, filter_name: str
) -> QuerySet[City] | NoReturn:
    """
    Оставляет в queryset только значения, удовлетворяющие фильтру filter.
    Вызывает соответствующую функцию фильтрации из FILTER_FUNCTIONS.

    :param queryset: Исходный QuerySet городов.
    :param user: Пользователь, для которого применяется фильтр.
    :param filter_name: Название фильтра.
    :return: Отфильтрованный QuerySet.
    """
    func = FILTER_FUNCTIONS.get(filter_name)
    if not func:
        raise KeyError(f'Неизвестный фильтр: {filter_name}')

    return func(queryset, user)


def filter_has_magnet(queryset: QuerySet[City], user: AbstractBaseUser) -> QuerySet[City]:
    """
    Фильтр оставляет только посещённые города, из которых имеется сувенир.

    Аргумент user не используется и нужен только для унификации функций фильтрации.
    """
    return queryset.filter(has_magnet=True, is_visited=True)


def filter_has_no_magnet(queryset: QuerySet[City], user: AbstractBaseUser) -> QuerySet[City]:
    """
    Фильтр оставляет только посещённые города, из которых нет сувенира.

    Аргумент user не используется и нужен только для унификации функций фильтрации.
    """
    return queryset.filter(has_magnet=False, is_visited=True)


def filter_visited(queryset: QuerySet[City], user: AbstractBaseUser) -> QuerySet[City]:
    """
    Фильтр оставляет только посещённые города.

    Аргумент user не используется и нужен только для унификации функций фильтрации.
    """
    return queryset.filter(is_visited=True)


def filter_not_visited(queryset: QuerySet[City], user: AbstractBaseUser) -> QuerySet[City]:
    """
    Фильтр оставляет только не посещённые города.

    Аргумент user не используется и нужен только для унификации функций фильтрации.
    """
    return queryset.filter(is_visited=False)


def filter_by_year(queryset: QuerySet[City], user: AbstractBaseUser, year: int) -> QuerySet[City]:
    return (
        queryset.annotate(
            visit_dates=ArrayAgg(
                'visitedcity__date_of_visit',
                filter=Q(visitedcity__user=user, visitedcity__date_of_visit__year=year),
                distinct=True,
                ordering='visitedcity__date_of_visit',
            ),
            first_visit_date=Min(
                'visitedcity__date_of_visit',
                filter=Q(visitedcity__user=user, visitedcity__date_of_visit__year=year),
            ),
            last_visit_date=Max(
                'visitedcity__date_of_visit',
                filter=Q(visitedcity__user=user, visitedcity__date_of_visit__year=year),
            ),
        )
        .exclude(Q(visit_dates=[]))
        .annotate(number_of_visits=ArrayLength('visit_dates'))
    )


def filter_current_year(queryset: QuerySet[City], user: AbstractBaseUser) -> QuerySet[City]:
    """
    Фильтр оставляет только города, посещённые в текущем году.
    Также обновляет поля visit_dates, first_visit_date, last_visit_date и number_of_visits,
    учитывая только посещения за текущий год.
    """
    current_year = datetime.today().year
    return filter_by_year(queryset, user, current_year)


def filter_last_year(queryset: QuerySet[City], user: AbstractBaseUser) -> QuerySet[City]:
    """
    Фильтр оставляет только города, посещённые в прошлом году.
    Также обновляет поля visit_dates, first_visit_date и last_visit_date,
    учитывая только посещения за прошлый год.
    """
    previous_year = datetime.today().year - 1
    return filter_by_year(queryset, user, previous_year)


FILTER_FUNCTIONS: dict[str, Callable[[QuerySet[City], AbstractBaseUser], QuerySet[City]]] = {
    'magnet': filter_has_magnet,
    'no_magnet': filter_has_no_magnet,
    'current_year': filter_current_year,
    'last_year': filter_last_year,
    'visited': filter_visited,
    'not_visited': filter_not_visited,
}
