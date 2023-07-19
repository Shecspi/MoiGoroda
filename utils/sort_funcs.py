from django.db.models import QuerySet, F


def sort_validation(sort_value: str, valid_sorts: tuple) -> str | bool:
    """
    Проверяет, что значение `sort_value` является одним из значений кортежа `valid_sorts`.
    """
    if sort_value in valid_sorts:
        return sort_value
    else:
        return False


def apply_sort(queryset: QuerySet, sort_value: str = '') -> QuerySet:
    """
    Добавляет к `queryset` фильтрация, на основе `sort_value`.
    Не проверяет корреткность `sort_value`.
    Если `sort_value` не передан, то применяется сортировка по умолчанию.
    """
    match sort_value:
        case 'name_down':
            queryset = queryset.order_by('title')
        case 'name_up':
            queryset = queryset.order_by('-title')
        case 'date_down':
            queryset = queryset.order_by('is_visited', '-date_of_visit')
        case 'date_up':
            queryset = queryset.order_by('is_visited', 'date_of_visit')
        case _:
            queryset = queryset.order_by('-is_visited', '-date_of_visit', 'title')

    return queryset
