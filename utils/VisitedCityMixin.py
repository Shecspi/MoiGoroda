from datetime import datetime

from django.db.models import QuerySet


class VisitedCityMixin:
    def apply_filter_to_queryset(self, queryset: QuerySet) -> QuerySet:
        match self.filter:
            case 'magnet':
                queryset = queryset.filter(has_magnet=False)
            case 'current_year':
                queryset = queryset.filter(date_of_visit__year=datetime.now().year)
            case 'last_year':
                queryset = queryset.filter(date_of_visit__year=datetime.now().year - 1)

        return queryset

    def _apply_sort_to_queryset(self, queryset: QuerySet) -> QuerySet:
        # ToDo Sort инициализируется в классе уровнем выше. Нужно передавать как аргумент метода.
        match self.sort:
            case 'name_down':
                queryset = queryset.order_by('city__title')
            case 'name_up':
                queryset = queryset.order_by('-city__title')
            case 'date_down':
                queryset = queryset.order_by('date_of_visit')
            case 'date_up':
                queryset = queryset.order_by('-date_of_visit')
            case _:
                queryset = queryset.order_by('-date_of_visit', 'city__title')

        return queryset

    def check_validity_of_filter_value(self, filter_value: str) -> str | None:
        if filter_value in self.valid_filters:
            return filter_value
        else:
            return None

    def _check_validity_of_sort_value(self, sort_value: str) -> str | None:
        if sort_value in self.valid_sorts:
            return sort_value
        else:
            return None


