"""
Реализует методы для работы с фильтрами и сортировкой для страницы городов региона.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


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
        @param filter_value: Значение фильтра, может быть пустой строкой.
        @param sort_value: Значение сортировки, может быть пустой строкой
        """
        url_params = []
        valid_filters = ['has_magnet', 'has_no_magnet', 'current_year', 'last_year']
        valid_sorts = [
            'name_down',
            'name_up',
            'first_visit_date_down',
            'first_visit_date_up',
            'default_auth',
            'default_guest',
        ]

        if filter_value and filter_value in valid_filters:
            url_params.append(f'filter={filter_value}')
        if sort_value and sort_value in valid_sorts:
            url_params.append(f'sort={sort_value}')

        return '&'.join(url_params)
