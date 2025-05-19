"""
Реализует методы для работы с фильтрами и сортировкой для страницы городов региона.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


class CitiesByRegionMixin:
    @staticmethod
    def get_url_params(filter_value: str | None, sort_value: str | None) -> str | None:
        """
        Возвращает строку, пригодную для использования в URL-адресе после знака '?' с параметрами 'filter' и 'sort'
        @param filter_value: Значение фильтра, может быть пустой строкой.
        @param sort_value: Значение сортировки, может быть пустой строкой
        """
        url_params = []

        if filter_value:
            url_params.append(f'filter={filter_value}')
        if sort_value:
            url_params.append(f'sort={sort_value}')

        return '&'.join(url_params)
