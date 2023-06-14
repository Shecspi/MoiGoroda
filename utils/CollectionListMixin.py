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

    @staticmethod
    def apply_sort_to_queryset(queryset: QuerySet, sort_value: str) -> QuerySet:
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
