from django.db.models import F, QuerySet


class CollectionListMixin:
    @staticmethod
    def apply_filter_to_queryset(queryset: QuerySet, filter_value: str) -> QuerySet:
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

    @staticmethod
    def get_url_params(filter_value: str | None, sort_value: str | None) -> str | None:
        """
        Возвращает строку, пригодную для использования в URL-адресе после знака '?'
        с параметрами 'filter' и 'sort'
        @param filter_value: Значение фльтра, может быть пустой строкой.
        @param sort_value: Значение сортировки, может быть пустой строкой
        """
        url_params = []

        if filter_value:
            url_params.append(f'filter={filter_value}')
        if sort_value:
            url_params.append(f'sort={sort_value}')

        return '&'.join(url_params)


