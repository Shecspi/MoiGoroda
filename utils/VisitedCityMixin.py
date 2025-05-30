"""
Реализует методы для работы с фильтрами и сортировкой для страницы всех посещённых городов.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime

from django.db.models import QuerySet, F


class VisitedCityMixin:
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
            'first_visit_date_down',
            'first_visit_date_up',
            'last_visit_date_down',
            'last_visit_date_up',
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
            Может принимать одно из 5 значений:
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
                queryset = queryset.order_by(
                    F('date_of_visit').desc(nulls_last=True), 'city__title'
                )
            case _:
                raise KeyError(f'Неверный параметр "sort_value" - {sort_value}')

        return queryset
