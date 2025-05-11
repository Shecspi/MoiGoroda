import openpyxl
import pytest
from io import StringIO, BytesIO

from account.serializer import TxtSerializer, CsvSerializer, XlsSerializer, JsonSerializer


# Предположим, что TxtSerializer — это класс, который был импортирован


@pytest.fixture
def txt_sample_report() -> list[tuple[str, ...]]:
    return [
        ('Город', 'Регион', 'Количество посещений'),
        ('Москва', 'Москва', '5'),
        ('Жуков', 'Калужская область', '10'),
    ]


@pytest.fixture
def txt_serializer() -> TxtSerializer:
    return TxtSerializer()


# Тест для метода __get_max_length
def test_txt_get_max_length(txt_serializer: TxtSerializer, txt_sample_report):
    result = txt_serializer._TxtSerializer__get_max_length(txt_sample_report)
    assert result == [6, 17, 20]


# Тест для метода __get_formated_row
def test_txt_get_formated_row(txt_serializer: TxtSerializer):
    formatted_row = txt_serializer._TxtSerializer__get_formated_row(
        ('Жуков', 'Калужская область', '10'), [6, 17, 20]
    )
    assert formatted_row == 'Жуков      Калужская область     10                       \n'


# Тест для метода convert
def test_txt_convert(txt_serializer: TxtSerializer, txt_sample_report):
    # Мы можем напрямую проверить, что возвращаемое содержимое верно
    result = txt_serializer.convert(txt_sample_report)

    assert isinstance(result, StringIO)
    result.seek(0)
    content = result.read()

    expected_content = (
        'Город      Регион                Количество посещений     \n'
        'Москва     Москва                5                        \n'
        'Жуков      Калужская область     10                       \n'
    )
    assert content == expected_content


# Тест для метода content_type
def test_txt_content_type(txt_serializer: TxtSerializer):
    assert txt_serializer.content_type() == 'text/txt'


# Тест для метода filetype
def test_txt_filetype(txt_serializer: TxtSerializer):
    assert txt_serializer.filetype() == 'txt'


# Фикстура для предоставления тестовых данных
@pytest.fixture
def csv_sample_report() -> list[tuple[str, ...]]:
    return [
        ('Город', 'Регион', 'Количество посещений'),
        ('Москва', 'Москва', '5'),
        ('Жуков', 'Калужская область', '10'),
    ]


@pytest.fixture
def csv_serializer() -> CsvSerializer:
    return CsvSerializer()


# Тест для метода convert
def test_csv_convert(csv_serializer: CsvSerializer, csv_sample_report):
    # Проверяем, что метод convert генерирует корректный CSV файл
    result = csv_serializer.convert(csv_sample_report)

    assert isinstance(result, StringIO)
    result.seek(0)
    content = result.read()

    expected_content = (
        'Город,Регион,Количество посещений\n' 'Москва,Москва,5\n' 'Жуков,Калужская область,10\n'
    )
    assert content == expected_content


# Тест для метода content_type
def test_csv_content_type(csv_serializer: CsvSerializer):
    assert csv_serializer.content_type() == 'text/csv'


# Тест для метода filetype
def test_csv_filetype(csv_serializer: CsvSerializer):
    assert csv_serializer.filetype() == 'csv'


# Фикстура для предоставления тестовых данных
@pytest.fixture
def xls_sample_report() -> list[tuple[str, ...]]:
    return [
        ('Город', 'Регион', 'Количество посещений'),
        ('Москва', 'Москва', '5'),
        ('Жуков', 'Калужская область', '10'),
    ]


@pytest.fixture
def xls_serializer() -> XlsSerializer:
    return XlsSerializer()


# Тест для метода convert
def test_xls_convert(xls_serializer: XlsSerializer, xls_sample_report):
    # Проверяем, что метод convert генерирует корректный Excel файл
    result = xls_serializer.convert(xls_sample_report)

    assert isinstance(result, BytesIO)
    result.seek(0)

    # Открываем созданный файл как Excel
    workbook = openpyxl.load_workbook(result)
    worksheet = workbook.active

    # Проверяем, что данные записаны корректно
    assert worksheet['A1'].value == 'Город'
    assert worksheet['B1'].value == 'Регион'
    assert worksheet['C1'].value == 'Количество посещений'

    assert worksheet['A2'].value == 'Москва'
    assert worksheet['B2'].value == 'Москва'
    assert worksheet['C2'].value == '5'

    assert worksheet['A3'].value == 'Жуков'
    assert worksheet['B3'].value == 'Калужская область'
    assert worksheet['C3'].value == '10'


# Тест для метода content_type
def test_xls_content_type(xls_serializer: XlsSerializer):
    assert xls_serializer.content_type() == 'application/vnd.ms-excel'


# Тест для метода filetype
def test_xls_filetype(xls_serializer: XlsSerializer):
    assert xls_serializer.filetype() == 'xls'


@pytest.fixture
def json_sample_report() -> list[tuple[str, ...]]:
    return [
        ('Город', 'Регион', 'Количество посещений'),
        ('Москва', 'Москва', '5'),
        ('Жуков', 'Калужская область', '10'),
    ]


@pytest.fixture
def json_serializer() -> JsonSerializer:
    return JsonSerializer()


# Тест для метода convert
def test_json_convert(json_serializer: JsonSerializer, json_sample_report):
    # Проверяем, что метод convert генерирует корректный JSON
    result = json_serializer.convert(json_sample_report)

    assert isinstance(result, StringIO)
    result.seek(0)
    content = result.read()

    expected_content = """[
    [
        "Город",
        "Регион",
        "Количество посещений"
    ],
    [
        "Москва",
        "Москва",
        "5"
    ],
    [
        "Жуков",
        "Калужская область",
        "10"
    ]
]"""
    assert content == expected_content


# Тест для метода content_type
def test_json_content_type(json_serializer: JsonSerializer):
    assert json_serializer.content_type() == 'application/json'


# Тест для метода filetype
def test_json_filetype(json_serializer: JsonSerializer):
    assert json_serializer.filetype() == 'json'
