from typing import Callable, NoReturn

from django.db.models import QuerySet, F

from city.models import VisitedCity


def apply_sort_to_queryset(
    queryset: QuerySet[VisitedCity], sort_name: str
) -> QuerySet[VisitedCity] | NoReturn:
    """
    Производит сортировку QuerySet на основе параметра 'sort_name'.

    :param queryset: QuerySet, который необходимо отсортировать.
    :param sort_name: Строка, определяющая сортировку. Возможные значения:
        - 'name_down' — сортировка по названию от Я до А
        - 'name_up' — сортировка по названию от А до Я
        - 'first_visit_date_down' — сначала города с более поздней датой первого посещения
        - 'first_visit_date_up' — сначала города без указания даты, далее давно посещённые и в конце недавно посещённые
        - 'last_visit_date_down' — сначала города с более поздней датой последнего посещения
        - 'last_visit_date_up' — сначала города без указания даты, далее давно посещённые и в конце недавно посещённые
        - 'default_auth' — сортировка по умолчанию для авторизованных пользователей
    :return: Отсортированный QuerySet или KeyError, если передан некорректный параметр `sort_name`.
    """
    func = SORT_FUNCTIONS.get(sort_name)
    if not func:
        raise KeyError(f'Неизвестный параметр сортировки: {sort_name}')

    return func(queryset)


def sort_by_name_up(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    """Сортирует по названию (А → Я)."""
    return queryset.order_by('city__title')


def sort_by_name_down(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    """Сортирует по названию (Я → А)."""
    return queryset.order_by('-city__title')


def sort_by_first_visit_date_down(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    """Сначала города с более поздней датой первого посещения"""
    return queryset.order_by(F('first_visit_date').desc(nulls_last=True), 'city__title')


def sort_by_first_visit_date_up(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    """Сначала города без указания даты, далее давно посещённые и в конце недавно посещённые"""
    return queryset.order_by(F('first_visit_date').asc(nulls_first=True), 'city__title')


def sort_by_last_visit_date_down(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    """Сначала города с более поздней датой последнего посещения"""
    return queryset.order_by(F('last_visit_date').desc(nulls_last=True), 'city__title')


def sort_by_last_visit_date_up(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    """Сначала города без указания даты, далее давно посещённые и в конце недавно посещённые"""
    return queryset.order_by(F('last_visit_date').asc(nulls_first=True), 'city__title')


def sort_number_of_visits_down(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    """Сначала города с большим количеством посещений"""
    return queryset.order_by(F('number_of_visits').desc(nulls_last=True), 'city__title')


def sort_number_of_visits_up(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    """Сначала города с меньшим количеством посещений"""
    return queryset.order_by(F('number_of_visits').asc(nulls_first=True), 'city__title')


def date_of_foundation_down(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    return queryset.order_by(F('city__date_of_foundation').desc(nulls_last=True), 'city__title')


def date_of_foundation_up(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    return queryset.order_by(F('city__date_of_foundation').asc(nulls_last=True), 'city__title')


def number_of_users_who_visit_city_down(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    return queryset.order_by(
        F('number_of_users_who_visit_city').desc(nulls_last=True), 'city__title'
    )


def number_of_users_who_visit_city_up(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    return queryset.order_by(
        F('number_of_users_who_visit_city').asc(nulls_last=True), 'city__title'
    )


def number_of_visits_all_users_down(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    return queryset.order_by(F('number_of_visits_all_users').desc(nulls_last=True), 'city__title')


def number_of_visits_all_users_up(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    return queryset.order_by(F('number_of_visits_all_users').asc(nulls_last=True), 'city__title')


SORT_FUNCTIONS: dict[str, Callable[[QuerySet[VisitedCity]], QuerySet[VisitedCity]]] = {
    'name_down': sort_by_name_down,
    'name_up': sort_by_name_up,
    'first_visit_date_down': sort_by_first_visit_date_down,
    'first_visit_date_up': sort_by_first_visit_date_up,
    'last_visit_date_down': sort_by_last_visit_date_down,
    'last_visit_date_up': sort_by_last_visit_date_up,
    'number_of_visits_down': sort_number_of_visits_down,
    'number_of_visits_up': sort_number_of_visits_up,
    'date_of_foundation_down': date_of_foundation_down,
    'date_of_foundation_up': date_of_foundation_up,
    'number_of_users_who_visit_city_down': number_of_users_who_visit_city_down,
    'number_of_users_who_visit_city_up': number_of_users_who_visit_city_up,
    'number_of_visits_all_users_down': number_of_visits_all_users_down,
    'number_of_visits_all_users_up': number_of_visits_all_users_up,
}
