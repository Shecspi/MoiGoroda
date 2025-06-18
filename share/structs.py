from enum import StrEnum, auto


class TypeOfSharedPage(StrEnum):
    """
    Структура данных, которая хранит в себе информацию о трёх возможных типах отображаемых страниц.
    """

    dashboard = auto()
    city_map = auto()
    region_map = auto()
