from datetime import datetime

from django.db.models import QuerySet, F
from utils.SortFilterMixin import SortFilterMixin


class VisitedCityMixin(SortFilterMixin):
    @staticmethod
    def apply_sort_to_queryset(queryset: QuerySet, sort_value: str) -> QuerySet:
        """
        Производит сортировку QuerySet на основе данных в 'sort_value'.

        @param queryset: QuerySet, который необходимо отсортировать.
        @param sort_value: Параметр, на основе которого происходит сортировка.
            Может принимать одно из 6 значений:
                - 'name_down' - по названию по возрастанию
                - 'name_up' - по названию по убыванию
                - 'date_down' - сначала недавно посещённые
                - 'date_up'. - сначала давно посещённые
                - 'default' - значение по-умолчанию
        @return: Отсортированный QuerySet или KeyError, если передан некорректный параметр `sort_value`.
        """
        match sort_value:
            case 'name_down':
                queryset = queryset.order_by('city__title')
            case 'name_up':
                queryset = queryset.order_by('-city__title')
            case 'date_down':
                queryset = queryset.order_by(F('date_of_visit').asc(nulls_first=True))
            case 'date_up':
                queryset = queryset.order_by(F('date_of_visit').desc(nulls_last=True))
            case 'default':
                queryset = queryset.order_by(F('date_of_visit').desc(nulls_last=True), 'city__title')
            case _:
                raise KeyError('Неверный параметр `sort_value`')

        return queryset


