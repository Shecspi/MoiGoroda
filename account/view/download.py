import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from io import StringIO, BytesIO
from typing import Literal

import openpyxl
from django.http import HttpResponse, Http404

from services.db.area_repo import get_visited_areas
from services.db.regions_repo import get_all_visited_regions
from services.db.visited_city_repo import get_all_visited_cities


class Report(ABC):
    @abstractmethod
    def __init__(self, user_id: int) -> None:
        ...

    @abstractmethod
    def get_report(self) -> list[tuple]:
        ...


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
                (city.city.title, str(city.region), str(city.date_of_visit), str(city.has_magnet), str(city.rating)),
            )
        return result


class RegionReport(Report):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def get_report(self) -> list[tuple]:
        regions = get_all_visited_regions(self.user_id)
        result = [
            ('Регион', 'Всего городов', 'Посещено городов, шт', 'Посещено городов, %', 'Осталось посетить, шт'),
        ]
        for region in regions:
            result.append(
                (region, 10, 5, 50, 5)
            )
        return result


class Serializer(ABC):
    @abstractmethod
    def convert(self, report):
        ...

    @abstractmethod
    def content_type(self):
        ...

    @abstractmethod
    def filetype(self):
        ...


class TxtSerializer(Serializer):
    def convert(self, report: list[tuple]) -> StringIO:
        buffer = StringIO()
        for line in report:
            buffer.write(f'{" --- ||| --- ".join([item for item in line])}\n')
        return buffer

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


class AreaReport(Report):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def get_report(self) -> list:
        areas = get_visited_areas(self.user_id)
        result = [
            ('Федеральный округ', 'Всего регионов, шт', 'Посещено регионов, шт',
             'Посещено регионов, %', 'Осталось посетить, шт'),
        ]
        for area in areas:
            result.append(
                (area.title, 5, 2, 40, 3),
            )
        return result


def download(request):
    if request.method == 'POST':
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
        elif filetype == 'xls':
            buffer = XlsSerializer()
        else:
            raise Http404

    response = HttpResponse(buffer.convert(report.get_report()).getvalue(), content_type=buffer.content_type())
    filename = f'MoiGoroda__{request.user}__{int(datetime.now().timestamp())}'
    response['Content-Disposition'] = f'attachment; filename={filename}.{buffer.filetype()}'
    return response
