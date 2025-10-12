"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from abc import ABC, abstractmethod

from django.db.models import F

from city.services.db import get_unique_visited_cities, get_all_visited_cities
from city.services.sort import apply_sort_to_queryset
from services.db.area_repo import get_visited_areas
from region.services.db import get_all_region_with_visited_cities


class Report(ABC):
    @abstractmethod
    def __init__(self, user_id: int) -> None: ...

    @abstractmethod
    def get_report(self) -> list[tuple[str | int | float, ...]]: ...


class CityReport(Report):
    def __init__(self, user_id: int, group_city: bool = False) -> None:
        self.user_id = user_id
        self.group_city = group_city

    def get_report(self) -> list[tuple[str | int | float, ...]]:
        result: list[tuple[str | int | float, ...]]

        if self.group_city:
            all_visited_cities = get_unique_visited_cities(self.user_id)
            sorted_visited_cities = apply_sort_to_queryset(
                all_visited_cities, 'last_visit_date_down'
            )
            result = [
                (
                    'Город',
                    'Регион',
                    'Страна',
                    'Количество посещений',
                    'Дата первого посещения',
                    'Дата последнего посещения',
                    'Наличие сувенира',
                    'Средняя оценка',
                ),
            ]
            for city in sorted_visited_cities:
                result.append(
                    (
                        city.city.title,
                        str(city.city.region) if city.city.region else 'Нет региона',
                        str(city.city.country),
                        city.number_of_visits,  # type: ignore[attr-defined]
                        str(city.first_visit_date) if city.first_visit_date else 'Не указана',  # type: ignore[attr-defined]
                        str(city.last_visit_date) if city.last_visit_date else 'Не указана',  # type: ignore[attr-defined]
                        '+' if city.has_souvenir else '-',  # type: ignore[attr-defined]
                        city.average_rating if city.average_rating else '',  # type: ignore[attr-defined]
                    ),
                )
        else:
            all_visited_cities = get_all_visited_cities(self.user_id)
            sorted_visited_cities = all_visited_cities.order_by(
                F('date_of_visit').desc(nulls_last=True)
            )
            result = [
                (
                    'Город',
                    'Регион',
                    'Страна',
                    'Дата посещения',
                    'Наличие сувенира',
                    'Оценка',
                ),
            ]
            for city in sorted_visited_cities:
                result.append(
                    (
                        city.city.title,
                        str(city.city.region) if city.city.region else 'Нет региона',
                        str(city.city.country),
                        str(city.date_of_visit) if city.date_of_visit else 'Не указана',
                        '+' if city.has_magnet else '-',
                        city.rating if city.rating else '',
                    ),
                )

        return result


class RegionReport(Report):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def get_report(self) -> list[tuple[str | int | float, ...]]:
        regions = get_all_region_with_visited_cities(self.user_id)
        result: list[tuple[str | int | float, ...]] = [
            (
                'Регион',
                'Всего городов',
                'Посещено городов, шт',
                'Посещено городов, %',
                'Осталось посетить, шт',
            ),
        ]
        for region in regions:
            title = region
            num_total_cities = region.num_total  # type: ignore[attr-defined]
            num_visited_cities = region.num_visited  # type: ignore[attr-defined]
            try:
                ratio_visited_cities = f'{(num_visited_cities / num_total_cities):.0%}'
            except ZeroDivisionError:
                ratio_visited_cities = '0%'
            num_not_visited_cities = num_total_cities - num_visited_cities
            result.append(
                (
                    str(title),
                    num_total_cities,
                    num_visited_cities,
                    ratio_visited_cities,
                    num_not_visited_cities,
                ),
            )
        return result


class AreaReport(Report):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def get_report(self) -> list[tuple[str | int | float, ...]]:
        areas = get_visited_areas(self.user_id)
        result: list[tuple[str | int | float, ...]] = [
            (
                'Федеральный округ',
                'Всего регионов, шт',
                'Посещено регионов, шт',
                'Посещено регионов, %',
                'Осталось посетить, шт',
            ),
        ]
        for area in areas:
            title = area.title
            num_total_regions = area.total_regions
            num_visited_regions = area.visited_regions
            try:
                ratio_visited_regions = f'{(num_visited_regions / num_total_regions):.0%}'
            except ZeroDivisionError:
                ratio_visited_regions = '0%'
            num_not_visited_regions = num_total_regions - num_visited_regions
            result.append(
                (
                    str(title),
                    num_total_regions,
                    num_visited_regions,
                    ratio_visited_regions,
                    num_not_visited_regions,
                ),
            )
        return result
