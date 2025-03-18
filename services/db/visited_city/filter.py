from typing import Callable

from django.db.models import QuerySet
from mypy_extensions import NoReturn

from city.models import VisitedCity


def apply_filter_to_queryset(
    queryset: QuerySet[VisitedCity], filter_name: str
) -> QuerySet[VisitedCity] | NoReturn:
    func = FILTER_FUNCTIONS.get(filter_name)
    if not func:
        raise KeyError(f'Неизвестный фильтр: {filter_name}')

    return func(queryset)
    # match filter_value:
    #     case 'magnet':
    #         queryset = queryset.filter(has_magnet=False)
    #     case 'current_year':
    #         queryset = queryset.filter(date_of_visit__year=datetime.now().year)
    #     case 'last_year':
    #         queryset = queryset.filter(date_of_visit__year=datetime.now().year - 1)
    #     case _:
    #         raise KeyError
    #
    #     return queryset


def filter_has_magnet(queryset: QuerySet[VisitedCity]) -> QuerySet[VisitedCity]:
    """
    Фильтр оставляет только посещённые города, из которых имеется сувенир.
    В модели VisitedCity поле, содержащее информацию о сувенире, называется 'has_magnet',
    но в итоговом QuerySet оно меняется на 'has_souvenir'
    (которое является обобщённым для всех одинаковых посещённых городов),
    поэтому именно по нему происходит фильтрация.
    """
    return queryset.filter(has_souvenir=True)


FILTER_FUNCTIONS: dict[str, Callable[[QuerySet[VisitedCity]], QuerySet[VisitedCity]]] = {
    'magnet': filter_has_magnet,
    # 'has_no_magnet': filter_has_no_magnet,
    # 'current_year': filter_current_year,
    # 'last_year': filter_last_year,
}
