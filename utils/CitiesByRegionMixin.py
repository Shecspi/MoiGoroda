"""
Реализует методы для работы с фильтрами и сортировкой для страницы городов региона.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime

from django.db.models import QuerySet, F


class CitiesByRegionMixin:
    @staticmethod
    def declension_of_city(quantity: int) -> str:
        """
        Возвращает правильное склонение слова 'город' в зависимости от количества 'num'.
        """
        if quantity == 1:
            return 'город'
        elif 5 <= quantity <= 20:
            return 'городов'
        elif (
            len(str(quantity)) >= 2
            and 10 <= int(str(quantity)[-2:]) <= 20
            or str(quantity)[-1] in ['5', '6', '7', '8', '9', '0']
        ):
            return 'городов'
        elif str(quantity)[-1] in ['2', '3', '4']:
            return 'города'
        else:
            return 'город'

    @staticmethod
    def declension_of_visited(quantity: int) -> str:
        if len(str(quantity)) > 1 and str(quantity)[-2:] == '11':
            return 'Посещено'
        elif str(quantity)[-1] == '1':
            return 'Посещён'
        else:
            return 'Посещено'

    @staticmethod
    def get_url_params(filter_value: str | None, sort_value: str | None) -> str | None:
        """
        Возвращает строку, пригодную для использования в URL-адресе после знака '?' с параметрами 'filter' и 'sort'
        @param filter_value: Значение фльтра, может быть пустой строкой.
        @param sort_value: Значение сортировки, может быть пустой строкой
        """
        url_params = []
        valid_filters = ['magnet', 'current_year', 'last_year']
        valid_sorts = [
            'name_down',
            'name_up',
            'date_down',
            'date_up',
            'default_auth',
            'default_guest',
        ]

        if filter_value and filter_value in valid_filters:
            url_params.append(f'filter={filter_value}')
        if sort_value and sort_value in valid_sorts:
            url_params.append(f'sort={sort_value}')

        return '&'.join(url_params)

    @staticmethod
    def apply_filter_to_queryset(queryset: QuerySet, filter_value: str) -> QuerySet:
        match filter_value:
            case 'magnet':
                queryset = queryset.filter(has_magnet=False)
            case 'current_year':
                queryset = queryset.filter(date_of_visit__year=datetime.now().year)
            case 'last_year':
                queryset = queryset.filter(date_of_visit__year=datetime.now().year - 1)
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
                - 'date_down' - сначала недавно посещённые
                - 'date_up'. - сначала давно посещённые
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
                queryset = queryset.order_by(
                    '-is_visited', F('date_of_visit').asc(nulls_first=True)
                )
            case 'date_up':
                queryset = queryset.order_by(
                    '-is_visited', F('date_of_visit').desc(nulls_last=True)
                )
            case 'default_auth':
                queryset = queryset.order_by(
                    '-is_visited', F('date_of_visit').desc(nulls_last=True), 'title'
                )
            case 'default_guest':
                queryset = queryset.order_by('title')
            case _:
                raise KeyError

        return queryset
