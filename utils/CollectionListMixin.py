from typing import Any

from django.db.models import F, QuerySet
from utils.SortFilterMixin import SortFilterMixin


class CollectionListMixin(SortFilterMixin):
    @staticmethod
    def apply_filter_to_queryset(queryset: QuerySet[Any], filter_value: str) -> QuerySet[Any]:
        """
        Производит фильтрацию 'queryset' на основе значения 'filter'.

        @param queryset: QuerySet, к которому необходимо применить фильтр.
        @param filter_value: Параметр, на основе которого производится фильтрация.
            Может принимать одно из 2 значение:
                - 'not_started' - коллекции, в которых нет ни одного опсещённого города;
                - 'finished' - коллекции, в которых посещены все города.
        @return: Отфильтрованный QuerySet или KeyError, если передан некорректный параметр `filter_value`.
        """
        match filter_value:
            case 'not_started':
                queryset = queryset.filter(qty_of_visited_cities=0)
            case 'finished':
                queryset = queryset.filter(qty_of_visited_cities=F('qty_of_cities'))
            case _:
                raise KeyError

        return queryset

    @staticmethod
    def apply_sort_to_queryset(queryset: QuerySet[Any], sort_value: str) -> QuerySet[Any]:
        """
        Производит сортировку QuerySet на основе данных в 'sort_value'.

        @param queryset: QuerySet, который необходимо отсортировать.
        @param sort_value: Параметр, на основе которого происходит сортировка.
            Может принимать одно из 6 значений:
                - 'name_down' - по названию по возрастанию
                - 'name_up' - по названию по убыванию
                - 'progress_down' - сначала начатые
                - 'progress_up'. - сначала завершённые
                - 'default_auth' - по-умолчанию для авторизованного пользователя
                - 'default_guest' - по-умолчанию для неавторизованного пользователя
        @return: Отсортированный QuerySet или KeyError, если передан некорректный параметр `sort_value`.
        """
        match sort_value:
            case 'name_down':
                queryset = queryset.order_by('title')
            case 'name_up':
                queryset = queryset.order_by('-title')
            case 'progress_down':
                queryset = queryset.order_by('qty_of_visited_cities')
            case 'progress_up':
                queryset = queryset.order_by('-qty_of_visited_cities')
            case 'default_auth':
                queryset = queryset.order_by('-qty_of_visited_cities', 'title')
            case 'default_guest':
                queryset = queryset.order_by('-qty_of_cities', 'title')
            case _:
                raise KeyError('Неверный параметр `sort_value`')

        return queryset
