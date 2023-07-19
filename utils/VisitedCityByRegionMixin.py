from datetime import datetime

from django.db.models import QuerySet, F
from utils.SortFilterMixin import SortFilterMixin


class VisitedCityByRegionMixin(SortFilterMixin):
    def apply_filter_to_queryset(self, queryset: QuerySet) -> QuerySet:
        match self.filter:
            case 'magnet':
                queryset = queryset.filter(has_magnet=False)
            case 'current_year':
                queryset = queryset.filter(date_of_visit__year=datetime.now().year)
            case 'last_year':
                queryset = queryset.filter(date_of_visit__year=datetime.now().year - 1)

        return queryset

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
                - 'default' - по-умолчанию для страницы "Посещённые города"
                - 'default_auth' - по-умолчанию для авторизованного пользователя на странице "Города региона"
                - 'default_guest' - по-умолчанию для неавторизованного пользователя на странице "Города региона"
        @return: Отсортированный QuerySet или KeyError, если передан некорректный параметр `sort_value`.
        """
        match sort_value:
            case 'name_down':
                queryset = queryset.order_by('title')
            case 'name_up':
                queryset = queryset.order_by('-title')
            case 'date_down':
                queryset = queryset.order_by('-is_visited', F('date_of_visit').asc(nulls_first=True))
            case 'date_up':
                queryset = queryset.order_by('-is_visited', F('date_of_visit').desc(nulls_last=True))
            case 'default':
                queryset = queryset.order_by(F('date_of_visit').desc(nulls_last=True), 'city__title')
            case 'default_auth':
                queryset = queryset.order_by('-is_visited', F('date_of_visit').desc(nulls_last=True), 'title')
            case 'default_guest':
                queryset = queryset.order_by('title')
            case _:
                raise KeyError('Неверный параметр `sort_value`')

        return queryset

    def check_validity_of_filter_value(self, filter_value: str) -> str | None:
        if filter_value in self.valid_filters:
            return filter_value
        else:
            return None


