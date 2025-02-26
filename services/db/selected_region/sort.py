from typing import Callable, NoReturn

from django.db.models import QuerySet, F

from city.models import City


def apply_sort_to_queryset(queryset: QuerySet[City], sort_name: str) -> QuerySet[City] | NoReturn:
    """
    Производит сортировку QuerySet на основе параметра 'sort_name'.

    :param queryset: QuerySet, который необходимо отсортировать.
    :param sort_name: Строка, определяющая сортировку. Возможные значения:
        - 'name_down' — сортировка по названию от Я до А
        - 'name_up' — сортировка по названию от А до Я
        - 'first_visit_date_down' — сначала города с более поздней датой первого посещения
        - 'first_visit_date_up' — сначала города без указания даты, далее давно посещённые и в конце недавно посещённые
        - 'default_auth' — сортировка по умолчанию для авторизованных пользователей
    :return: Отсортированный QuerySet или KeyError, если передан некорректный параметр `sort_name`.
    """
    func = SORT_FUNCTIONS.get(sort_name)
    if not func:
        raise KeyError(f'Неизвестный параметр сортировки: {sort_name}')

    return func(queryset)


def sort_by_name_up(queryset: QuerySet) -> QuerySet:
    """Сортирует по названию (А → Я)."""
    return queryset.order_by('title')


def sort_by_name_down(queryset: QuerySet) -> QuerySet:
    """Сортирует по названию (Я → А)."""
    return queryset.order_by('-title')


def sort_by_first_visit_date_down(queryset: QuerySet) -> QuerySet:
    """Cначала города с более поздней датой первого посещения"""
    return queryset.order_by('-is_visited', F('first_visit_date').desc(nulls_last=True))


def sort_by_first_visit_date_up(queryset: QuerySet) -> QuerySet:
    """Cначала города без указания даты, далее давно посещённые и в конце недавно посещённые"""
    return queryset.order_by('-is_visited', F('first_visit_date').asc(nulls_first=True))


def sort_default_auth(queryset: QuerySet) -> QuerySet:
    """Сортировка по умолчанию для авторизованных пользователей"""
    return queryset.order_by('-is_visited', F('first_visit_date').desc(nulls_last=True), 'title')


SORT_FUNCTIONS: dict[str, Callable[[QuerySet[City]], QuerySet[City]]] = {
    'name_down': sort_by_name_down,
    'name_up': sort_by_name_up,
    'first_visit_date_down': sort_by_first_visit_date_down,
    'first_visit_date_up': sort_by_first_visit_date_up,
    'default_auth': sort_default_auth,
}
