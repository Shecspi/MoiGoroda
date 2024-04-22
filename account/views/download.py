"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import csv
import json
from abc import ABC, abstractmethod
from datetime import datetime
from io import StringIO, BytesIO
from typing import Sequence, Iterable

import openpyxl
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from services.db.area_repo import get_visited_areas
from services.db.regions_repo import get_all_visited_regions
from services.db.visited_city_repo import get_all_visited_cities


class Report(ABC):
    @abstractmethod
    def __init__(self, user_id: int) -> None: ...

    @abstractmethod
    def get_report(self) -> list[tuple]: ...


class CityReport(Report):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def get_report(self) -> list[tuple]:
        cities = get_all_visited_cities(self.user_id)
        result = [
            ('Город', 'Регион', 'Дата посещения', 'Наличие магнита', 'Оценка'),
        ]
        for city in cities:
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
            result.append(
                (str(area.title), str(5), str(2), str(40), str(3)),
            )
        return result


class Serializer(ABC):
    @abstractmethod
    def convert(self, report): ...

    @abstractmethod
    def content_type(self): ...

    @abstractmethod
    def filetype(self): ...


class TxtSerializer(Serializer):
    def convert(self, report: list[tuple[str]]) -> StringIO:
        buffer = StringIO()
        number_of_symbols = self.__get_max_length(report)
        for report_line in report:
            buffer.write(self.__get_formated_row(report_line, number_of_symbols))
        return buffer

    @staticmethod
    def __get_max_length(row: Sequence[Sequence]) -> list[int]:
        """
        Определяет максимальную длину элементов, расположенных в одном столбике многомерного массива.
        Возвращает список с максимальными длинами для каждого столбика.
        Количество элементов равно количеству столбиков в оригинальной итерируемом объекте.
        """
        number_of_symbols = []
        for index, value in enumerate(row[0]):
            number_of_symbols.append(len(max((x[index] for x in row), key=len)))
        return number_of_symbols

    @staticmethod
    def __get_formated_row(row: Sequence, number_of_symbols: Sequence[int]) -> str:
        formated_row = ''
        for index, value in enumerate(row):
            formated_row += f'{value:<{number_of_symbols[index] + 5}}'
        return formated_row + '\n'

    def content_type(self) -> str:
        return 'text/txt'

    def filetype(self) -> str:
        return 'txt'


class CsvSerializer(Serializer):
    def convert(self, report: list[tuple]) -> StringIO:
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer, delimiter=',', lineterminator='\r')
        for line in report:
            csv_writer.writerow([item for item in line])
        return csv_buffer

    def content_type(self) -> str:
        return 'text/csv'

    def filetype(self) -> str:
        return 'csv'


class XlsSerializer(Serializer):
    def convert(self, report: list[tuple]) -> BytesIO:
        workbook = openpyxl.Workbook()
        buffer = BytesIO()
        worksheet = workbook.active
        for line in report:
            worksheet.append(line)
        workbook.save(buffer)

        return buffer

    def content_type(self) -> str:
        return 'application/vnd.ms-excel'

    def filetype(self) -> str:
        return 'xls'


class JsonSerialixer(Serializer):
    def convert(self, report: list[tuple]) -> StringIO:
        buffer = StringIO()
        json.dump(report, buffer, indent=4, ensure_ascii=False)
        return buffer

    def content_type(self) -> str:
        return 'application/json'

    def filetype(self) -> str:
        return 'json'


@require_http_methods(['POST'])
@login_required()
def download(request):
    users_data = request.POST.dict()
    reporttype = users_data.get('reporttype')
    filetype = users_data.get('filetype')

    if reporttype == 'city':
        report = CityReport(request.user.id)
    elif reporttype == 'region':
        report = RegionReport(request.user.id)
    elif reporttype == 'area':
        report = AreaReport(request.user.id)
    else:
        raise Http404

    if filetype == 'txt':
        buffer = TxtSerializer()
    elif filetype == 'csv':
        buffer = CsvSerializer()
    elif filetype == 'json':
        buffer = JsonSerialixer()
    elif filetype == 'xls':
        buffer = XlsSerializer()
    else:
        raise Http404

    response = HttpResponse(
        buffer.convert(report.get_report()).getvalue(), content_type=buffer.content_type()
    )
    filename = f'MoiGoroda__{request.user}__{int(datetime.now().timestamp())}'
    response['Content-Disposition'] = f'attachment; filename={filename}.{buffer.filetype()}'
    return response
