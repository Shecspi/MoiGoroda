import csv
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from typing import Literal

from django.http import HttpResponse

from services.db.area_repo import get_visited_areas
from services.db.regions_repo import get_all_visited_regions
from services.db.visited_city_repo import get_all_visited_cities

"""
Города:
 - Название
 - Регион
 - Дата посещения
 - Наличие магнита
 - Оценка

Регионы:
 - Название
 - Всего городов
 - Посещено городов в штуках
 - Посещено городов в процентах
 
Округа:
 - Название
 - Всего регионов
 - Посещено регионов
"""


@dataclass
class CityFields:
    title: str
    region: str
    date_of_visit: datetime.date
    has_magnet: bool
    rating: int


@dataclass
class RegionFields:
    title: str
    number_of_cities: int
    number_of_visited_cities: int
    ratio_of_visited_cities: int
    number_of_not_visited_cities: int


@dataclass
class AreaFields:
    title: str
    number_of_regions: int
    number_of_visited_regions: int
    ratio_of_visited_regions: int
    number_of_not_visited_regions: int


class ReportTypeError(Exception):
    pass


def txt_serializer(user_id: int, reporttime: Literal['city', 'region', 'area']):
    buffer = StringIO()
    if reporttime == 'city':
        buffer.write(header_line_for_city())
        for city in get_prepared_visited_city_for_download(user_id):
            buffer.write(content_line_for_city(city))
    elif reporttime == 'region':
        buffer.write(header_line_for_region())
        for region in get_prepared_visited_regions_for_download(user_id):
            buffer.write(content_line_for_region(region))
    elif reporttime == 'area':
        buffer.write(header_line_for_area())
        for area in get_prepared_visited_areas_for_download(user_id):
            buffer.write(content_line_for_area(area))
    else:
        raise ReportTypeError('Неверно указан тип репорта')

    return buffer.getvalue()


def header_line_for_city():
    return (
        f"{str('Город'):<30}"
        f"{str('Регион'):<40}"
        f'{str('Дата посещения'):<20}'
        f'{str('Наличие магнита'):<20}'
        f'{str('Оценка'):<10}\n\n'
    )


def content_line_for_city(city: CityFields):
    return (
        f'{city.title:<30}'
        f'{str(city.region):<40}'
        f'{"Не указана" if not city.date_of_visit else str(city.date_of_visit):<20}'
        f'{"+" if city.has_magnet else "-":<20}'
        f'{"*" * city.rating:<10}\n'
    )


def header_line_for_region():
    return (
        f"{str('Регион'):<40}"
        f'{str('Всего городов'):<20}'
        f'{str('Посещено городов, шт'):<25}'
        f'{str('Посещено городов, %'):<25}'
        f'{str('Осталось посетить, шт'):<25}\n\n'
    )


def content_line_for_region(region: RegionFields):
    return (
        f"{region.title:<40}"
        f'{region.number_of_cities :<20}'
        f'{region.number_of_visited_cities:<25}'
        f'{region.ratio_of_visited_cities:<25}'
        f'{region.number_of_not_visited_cities:<25}\n'
    )


def header_line_for_area():
    return (
        f'{str('Федеральный округ'):<20}'
        f'{str('Всего регионов, шт'):<25}'
        f'{str('Посещено регионов, шт'):<25}'
        f'{str('Посещено регионов, %'):<25}'
        f'{str('Осталось посетить, шт'):<25}\n\n'
    )


def content_line_for_area(area: AreaFields):
    return (
        f'{area.title:<20}'
        f'{area.number_of_regions:<25}'
        f'{area.number_of_visited_regions:<25}'
        f'{area.ratio_of_visited_regions:<25}'
        f'{area.number_of_not_visited_regions:<25}\n'
    )


def csv_serializer(request):
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer, delimiter=',', lineterminator='\r')
    csv_writer.writerow(['Город', 'Регион', 'Дата посещения', 'Наличие магнита', 'Оценка'])
    for city in get_prepared_visited_city_for_download(1):
        csv_writer.writerow(
            [city.title, city.region, city.date_of_visit, city.has_magnet, city.rating]
        )

    return csv_buffer.getvalue()


def get_prepared_visited_city_for_download(user_id: int) -> list[CityFields]:
    cities = get_all_visited_cities(user_id)
    result = []
    for city in cities:
        result.append(
            CityFields(
                title=city.city.title,
                region=str(city.region),
                date_of_visit=city.date_of_visit,
                has_magnet=city.has_magnet,
                rating=city.rating,
            )
        )
    return result


def get_prepared_visited_regions_for_download(user_id: int) -> list[RegionFields]:
    regions = get_all_visited_regions(user_id)
    result = []
    for region in regions:
        result.append(
            RegionFields(
                title=region,
                number_of_cities=10,
                number_of_visited_cities=5,
                ratio_of_visited_cities=50,
                number_of_not_visited_cities=5
            )
        )
    return result


def get_prepared_visited_areas_for_download(user_id: int) -> list[AreaFields]:
    areas = get_visited_areas(user_id)
    result = []
    for area in areas:
        result.append(
            AreaFields(
                title=area.title,
                number_of_regions=5,
                number_of_visited_regions=2,
                ratio_of_visited_regions=40,
                number_of_not_visited_regions=3
            )
        )
    return result


def download(request):
    if request.method == 'POST':
        users_data = request.POST.dict()
        filetype = users_data.get('')

    download_file = csv_serializer(request)
    response = HttpResponse(download_file, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=myfile.csv'
    return response
