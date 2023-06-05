from datetime import datetime

from django.db.models import F, QuerySet


class CollectionListMixin:
    valid_filters = ['zero', 'all']
    valid_sorts = ['name_down', 'name_up', 'progress_down', 'progress_up']

    def check_validity_of_filter_value(self, filter_value: str) -> str | None:
        if filter_value in self.valid_filters:
            return filter_value
        else:
            return None

    def apply_filter_to_queryset(self, queryset: QuerySet, filter_value: str | None) -> QuerySet:
        match filter_value:
            case 'zero':
                queryset = queryset.filter(qty_of_visited_cities=0)
            case 'all':
                queryset = queryset.filter(qty_of_visited_cities=F('qty_of_cities'))

        return queryset

    def check_validity_of_sort_value(self, sort_value: str) -> str | None:
        if sort_value in self.valid_sorts:
            return sort_value
        else:
            return None

    def apply_sort_to_queryset(self, queryset: QuerySet, sort_value: str) -> QuerySet:
        match sort_value:
            case 'name_down':
                queryset = queryset.order_by('title')
            case 'name_up':
                queryset = queryset.order_by('-title')
            case 'progress_down':
                queryset = queryset.order_by('qty_of_visited_cities')
            case 'progress_up':
                queryset = queryset.order_by('-qty_of_visited_cities')
            case _:
                queryset = queryset.order_by('-qty_of_visited_cities', 'title')

        return queryset
