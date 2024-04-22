"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from abc import ABC, abstractmethod

from django.db.models import F

from services.db.area_repo import get_visited_areas
from services.db.regions_repo import get_all_visited_regions
from services.db.visited_city_repo import get_all_visited_cities, order_by_date_of_visit_desc


class Report(ABC):
    @abstractmethod
    def __init__(self, user_id: int) -> None: ...

    @abstractmethod
    def get_report(self) -> list[tuple]: ...


class CityReport(Report):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def get_report(self) -> list[tuple]:
        all_visited_cities = get_all_visited_cities(self.user_id)
        sorted_visited_cities = order_by_date_of_visit_desc(all_visited_cities)
        result = [
            ('Город', 'Регион', 'Дата посещения', 'Наличие магнита', 'Оценка'),
        ]
        for city in sorted_visited_cities:
            result.append(
                (
                    city.city.title,
                    str(city.region),
                    str(city.date_of_visit) if city.date_of_visit else 'Не указана',
                    '+' if city.has_magnet else '-',
                    '*' * city.rating if city.rating else '',
                ),
            )
        return result


class RegionReport(Report):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def get_report(self) -> list[tuple[str, ...]]:
        regions = get_all_visited_regions(self.user_id)
        result = [
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
            num_total_cities = region.num_total
            num_visited_cities = region.num_visited
            ratio_visited_cities = f'{(num_visited_cities / num_total_cities):.0%}'
            num_not_visited_cities = num_total_cities - num_visited_cities
            result.append(
                (
                    str(title),
                    str(num_total_cities),
                    str(num_visited_cities),
                    ratio_visited_cities,
                    str(num_not_visited_cities)
                ),
            )
        return result


class AreaReport(Report):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def get_report(self) -> list[tuple[str, ...]]:
        areas = get_visited_areas(self.user_id)
        result = [
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
            ratio_visited_regions = f'{(num_visited_regions / num_total_regions):.0%}'
            num_not_visited_regions = num_total_regions - num_visited_regions
            result.append(
                (
                    str(title),
                    str(num_total_regions),
                    str(num_visited_regions),
                    str(ratio_visited_regions),
                    str(num_not_visited_regions)
                ),
            )
        return result
