"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import csv
import json
from abc import ABC, abstractmethod
from io import StringIO, BytesIO
from typing import Sequence

import openpyxl


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
