from types import SimpleNamespace

import pytest

from city.dto import CityDetailsDTO


def make_city(title='Москва', region='Московская область', country='Россия'):
    return SimpleNamespace(title=title, region=region, country=country)


@pytest.mark.parametrize(
    'region, expected',
    [
        ('Московская область', 'Москва, Московская область, Россия - информация о городе, карта'),
        (None, 'Москва, Россия - информация о городе, карта'),
    ],
)
def test_page_title(region, expected):
    city = make_city(region=region)
    dto = CityDetailsDTO(
        city=city,
        average_rating=0.0,
        popular_months=[],
        visits=[],
        collections=[],
        number_of_visits=0,
        number_of_visits_all_users=0,
    )

    assert dto.page_title == expected


def test_page_description_minimal():
    city = make_city(region=None)
    dto = CityDetailsDTO(
        city=city,
        average_rating=0.0,
        popular_months=[],
        visits=[],
        collections=[],
        number_of_visits=0,
        number_of_visits_all_users=0,
    )

    assert dto.page_description == (
        'Москва, Россия. '
        'Смотрите информацию о городе и карту на сайте «Мои Города». '
        'Зарегистрируйтесь, чтобы отмечать посещённые города.'
    )


def test_page_description_with_one_collection():
    city = make_city()

    class FakeCollection:
        def __str__(self):
            return 'Культурное наследие'

    collection = FakeCollection()
    dto = CityDetailsDTO(
        city=city,
        average_rating=0.0,
        popular_months=[],
        visits=[],
        collections=[collection],
        number_of_visits=0,
        number_of_visits_all_users=0,
    )

    assert 'Входит в коллекцию «Культурное наследие»' in dto.page_description


def test_page_description_with_multiple_collections():
    city = make_city()

    class Collection1:
        def __str__(self):
            return 'Исторические города'

    class Collection2:
        def __str__(self):
            return 'Морские курорты'

    collections = [Collection1(), Collection2()]
    dto = CityDetailsDTO(
        city=city,
        average_rating=0.0,
        popular_months=[],
        visits=[],
        collections=collections,
        number_of_visits=0,
        number_of_visits_all_users=0,
    )

    assert 'Входит в коллекции «Исторические города», «Морские курорты»' in dto.page_description


def test_page_description_with_rating():
    city = make_city()
    dto = CityDetailsDTO(
        city=city,
        average_rating=4.7,
        popular_months=[],
        visits=[],
        collections=[],
        number_of_visits=0,
        number_of_visits_all_users=0,
    )

    assert 'Средняя оценка путешественников — 4.7' in dto.page_description


def test_page_description_with_popular_months():
    city = make_city()
    dto = CityDetailsDTO(
        city=city,
        average_rating=0.0,
        popular_months=['Июнь', 'Июль'],
        visits=[],
        collections=[],
        number_of_visits=0,
        number_of_visits_all_users=0,
    )

    assert 'Лучшее время для поездки: Июнь, Июль' in dto.page_description


def test_page_description_full():
    city = make_city()

    class Collection1:
        def __str__(self):
            return 'Города России'

    class Collection2:
        def __str__(self):
            return 'Места силы'

    collections = [Collection1(), Collection2()]
    dto = CityDetailsDTO(
        city=city,
        average_rating=4.5,
        popular_months=['Май', 'Сентябрь'],
        visits=[],
        collections=collections,
        number_of_visits=3,
        number_of_visits_all_users=150,
    )

    desc = dto.page_description

    assert 'Москва, Московская область, Россия' in desc
    assert 'Входит в коллекции «Города России», «Места силы»' in desc
    assert 'Средняя оценка путешественников — 4.5' in desc
    assert 'Лучшее время для поездки: Май, Сентябрь' in desc
    assert 'Зарегистрируйтесь, чтобы отмечать посещённые города' in desc
