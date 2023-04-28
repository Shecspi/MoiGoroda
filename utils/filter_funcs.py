from datetime import datetime

from django.db.models import QuerySet


def filter_validation(filter_value: str, valid_filters: tuple) -> str | bool:
    """
    Проверяет, что значение `filter_value` является одним из значений кортежа `valid_filters`.
    """
    if filter_value in valid_filters:
        return filter_value
    else:
        return False


def apply_filter(queryset: QuerySet, filter_value: str) -> QuerySet:
    """
    Добавляет к `queryset` фильтрация, на основе `filter_value`.
    Не проверяет корреткность `filter_value`.
    """
    match filter_value:
        case 'magnet':
            queryset = queryset.filter(has_magnet=False)
        case 'current_year':
            queryset = queryset.filter(date_of_visit__year=datetime.now().year)
        case 'last_year':
            queryset = queryset.filter(date_of_visit__year=datetime.now().year - 1)

    return queryset
