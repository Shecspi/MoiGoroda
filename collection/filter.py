"""
Фильтрация городов в коллекциях.

Этот модуль предоставляет механизм применения фильтров к QuerySet объектов модели City.
В настоящий момент реализованы фильтры для получения посещённых и непосещённых городов.

Доступные фильтры:
- 'visited': только посещённые города
- 'not_visited': только непосещённые города
"""

from typing import NoReturn, Callable

from django.db.models import QuerySet

from city.models import City


def apply_filter_to_queryset(
    queryset: QuerySet[City], filter_name: str
) -> QuerySet[City] | NoReturn:
    """
    Применяет указанный фильтр к QuerySet городов.

    Фильтр определяется по имени, переданному в filter_name, и выбирается из словаря FILTER_FUNCTIONS.
    Если фильтр не найден, возбуждается исключение KeyError.

    :param queryset: Исходный QuerySet объектов City.
    :param filter_name: Имя фильтра (например, 'visited' или 'not_visited').
    :return: Отфильтрованный QuerySet объектов City.
    :raises KeyError: Если фильтр с указанным именем не найден.
    """
    func = FILTER_FUNCTIONS.get(filter_name)
    if not func:
        raise KeyError(f'Неизвестный фильтр: {filter_name}')

    return func(queryset)


def filter_visited(queryset: QuerySet[City]) -> QuerySet[City]:
    """
    Возвращает только посещённые города из QuerySet.

    :param queryset: QuerySet объектов City.
    :return: QuerySet с городами, у которых is_visited=True.
    """
    return queryset.filter(is_visited=True)  # type: ignore[misc]


def filter_not_visited(queryset: QuerySet[City]) -> QuerySet[City]:
    """
    Возвращает только непосещённые города из QuerySet.

    :param queryset: QuerySet объектов City.
    :return: QuerySet с городами, у которых is_visited=False.
    """
    return queryset.filter(is_visited=False)  # type: ignore[misc]


FILTER_FUNCTIONS: dict[str, Callable[[QuerySet[City]], QuerySet[City]]] = {
    'visited': filter_visited,
    'not_visited': filter_not_visited,
}
