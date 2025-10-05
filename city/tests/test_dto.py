from types import SimpleNamespace
from typing import Any, Protocol

import pytest

from city.dto import CityDetailsDTO


class MockCity(Protocol):
    title: str
    region: str | None
    country: str


def make_city(
    title: str = 'Москва', region: str | None = 'Московская область', country: str = 'Россия'
) -> SimpleNamespace:
    # region может быть None для тестов, где это требуется
    return SimpleNamespace(title=title, region=region, country=country)


def make_city_details_dto(
    city: Any | None = None,
    average_rating: float = 0.0,
    popular_months: list[str] | None = None,
    visits: list[dict[str, Any]] | None = None,
    collections: list[Any] | None = None,
    number_of_visits: int = 0,
    number_of_visits_all_users: int = 0,
    number_of_users_who_visit_city: int = 0,
    number_of_cities_in_country: int = 0,
    number_of_cities_in_region: int = 0,
    rank_in_country_by_visits: int = 0,
    rank_in_country_by_users: int = 0,
    rank_in_region_by_visits: int = 0,
    rank_in_region_by_users: int = 0,
    neighboring_cities_by_rank_in_country_by_visits: list[Any] | None = None,
    neighboring_cities_by_rank_in_country_by_users: list[Any] | None = None,
    neighboring_cities_by_rank_in_region_by_visits: list[Any] | None = None,
    neighboring_cities_by_rank_in_region_by_users: list[Any] | None = None,
) -> CityDetailsDTO:
    if city is None:
        city = make_city()
    if popular_months is None:
        popular_months = []
    if visits is None:
        visits = []
    if collections is None:
        collections = []
    if neighboring_cities_by_rank_in_country_by_visits is None:
        neighboring_cities_by_rank_in_country_by_visits = []
    if neighboring_cities_by_rank_in_country_by_users is None:
        neighboring_cities_by_rank_in_country_by_users = []
    if neighboring_cities_by_rank_in_region_by_visits is None:
        neighboring_cities_by_rank_in_region_by_visits = []
    if neighboring_cities_by_rank_in_region_by_users is None:
        neighboring_cities_by_rank_in_region_by_users = []

    return CityDetailsDTO(
        city=city,  # type: ignore
        average_rating=average_rating,
        popular_months=popular_months,
        visits=visits,
        collections=collections,
        number_of_visits=number_of_visits,
        number_of_visits_all_users=number_of_visits_all_users,
        number_of_users_who_visit_city=number_of_users_who_visit_city,
        number_of_cities_in_country=number_of_cities_in_country,
        number_of_cities_in_region=number_of_cities_in_region,
        rank_in_country_by_visits=rank_in_country_by_visits,
        rank_in_country_by_users=rank_in_country_by_users,
        rank_in_region_by_visits=rank_in_region_by_visits,
        rank_in_region_by_users=rank_in_region_by_users,
        neighboring_cities_by_rank_in_country_by_visits=neighboring_cities_by_rank_in_country_by_visits,
        neighboring_cities_by_rank_in_country_by_users=neighboring_cities_by_rank_in_country_by_users,
        neighboring_cities_by_rank_in_region_by_visits=neighboring_cities_by_rank_in_region_by_visits,
        neighboring_cities_by_rank_in_region_by_users=neighboring_cities_by_rank_in_region_by_users,
    )


@pytest.mark.parametrize(
    'region, expected',
    [
        ('Московская область', 'Москва, Московская область, Россия - информация о городе, карта'),
        (None, 'Москва, Россия - информация о городе, карта'),
    ],
)
def test_page_title(region: str | None, expected: str) -> None:
    city = make_city(region=region)
    dto = make_city_details_dto(city=city)

    assert dto.page_title == expected


def test_page_description_minimal() -> None:
    city = make_city(region=None)
    dto = make_city_details_dto(city=city)
    assert dto.page_description == (
        'Москва, Россия. '
        'Смотрите информацию о городе и карту на сайте «Мои Города». '
        'Зарегистрируйтесь, чтобы отмечать посещённые города.'
    )


def test_page_description_with_one_collection() -> None:
    city = make_city()

    class FakeCollection:
        def __str__(self) -> str:
            return 'Культурное наследие'

    collection = FakeCollection()
    dto = make_city_details_dto(city=city, collections=[collection])

    assert 'Входит в коллекцию «Культурное наследие»' in dto.page_description


def test_page_description_with_multiple_collections() -> None:
    city = make_city()

    class Collection1:
        def __str__(self) -> str:
            return 'Исторические города'

    class Collection2:
        def __str__(self) -> str:
            return 'Морские курорты'

    dto = make_city_details_dto(city=city, collections=[Collection1(), Collection2()])

    assert 'Входит в коллекции «Исторические города», «Морские курорты»' in dto.page_description


def test_page_description_with_rating() -> None:
    city = make_city()
    dto = make_city_details_dto(city=city, average_rating=4.7)

    assert 'Средняя оценка путешественников — 4.7' in dto.page_description


def test_page_description_with_popular_months() -> None:
    city = make_city()
    dto = make_city_details_dto(city=city, popular_months=['Июнь', 'Июль'])

    assert 'Лучшее время для поездки: Июнь, Июль' in dto.page_description


def test_page_description_full() -> None:
    city = make_city()

    class Collection1:
        def __str__(self) -> str:
            return 'Города России'

    class Collection2:
        def __str__(self) -> str:
            return 'Места силы'

    dto = make_city_details_dto(
        city=city,
        average_rating=4.5,
        popular_months=['Май', 'Сентябрь'],
        collections=[Collection1(), Collection2()],
        number_of_visits=3,
        number_of_visits_all_users=150,
    )

    desc = dto.page_description

    assert 'Москва, Московская область, Россия' in desc
    assert 'Входит в коллекции «Города России», «Места силы»' in desc
    assert 'Средняя оценка путешественников — 4.5' in desc
    assert 'Лучшее время для поездки: Май, Сентябрь' in desc
    assert 'Зарегистрируйтесь, чтобы отмечать посещённые города' in desc


def test_page_title_without_region() -> None:
    city = make_city(region=None)
    dto = make_city_details_dto(city=city)
    assert dto.page_title == 'Москва, Россия - информация о городе, карта'


def test_page_title_with_region() -> None:
    city = make_city(region='Свердловская область')
    dto = make_city_details_dto(city=city)
    assert dto.page_title == 'Москва, Свердловская область, Россия - информация о городе, карта'


def test_page_description_no_collections_no_rating_no_months() -> None:
    city = make_city(region=None)
    dto = make_city_details_dto(city=city, collections=[], average_rating=0, popular_months=[])
    desc = dto.page_description
    assert desc.startswith('Москва, Россия.')
    assert 'Входит в коллекцию' not in desc
    assert 'Средняя оценка' not in desc
    assert 'Лучшее время для поездки' not in desc


def test_page_description_one_collection() -> None:
    class Collection:
        def __str__(self) -> str:
            return 'Коллекция1'

    city = make_city()
    dto = make_city_details_dto(city=city, collections=[Collection()])
    desc = dto.page_description
    assert 'Входит в коллекцию «Коллекция1»' in desc


def test_page_description_multiple_collections_order() -> None:
    class CollectionA:
        def __str__(self) -> str:
            return 'Альфа'

    class CollectionB:
        def __str__(self) -> str:
            return 'Бета'

    city = make_city()
    dto = make_city_details_dto(city=city, collections=[CollectionA(), CollectionB()])
    desc = dto.page_description
    assert 'Входит в коллекции «Альфа», «Бета»' in desc


def test_page_description_with_zero_rating_and_popular_months_empty() -> None:
    city = make_city()
    dto = make_city_details_dto(city=city, average_rating=0, popular_months=[])
    desc = dto.page_description
    assert 'Средняя оценка путешественников' not in desc
    assert 'Лучшее время для поездки' not in desc


def test_page_description_with_rating_and_empty_popular_months() -> None:
    city = make_city()
    dto = make_city_details_dto(city=city, average_rating=3.3, popular_months=[])
    desc = dto.page_description
    assert 'Средняя оценка путешественников — 3.3' in desc
    assert 'Лучшее время для поездки' not in desc


def test_page_description_with_popular_months_and_zero_rating() -> None:
    city = make_city()
    dto = make_city_details_dto(city=city, average_rating=0, popular_months=['Январь'])
    desc = dto.page_description
    assert 'Лучшее время для поездки: Январь' in desc
    assert 'Средняя оценка путешественников' not in desc


def test_page_description_includes_base_text_always() -> None:
    city = make_city()
    dto = make_city_details_dto(city=city)
    assert 'Смотрите информацию о городе и карту на сайте «Мои Города».' in dto.page_description
    assert 'Зарегистрируйтесь, чтобы отмечать посещённые города.' in dto.page_description


def test_collections_str_called_once_per_collection() -> None:
    call_count: dict[str, int] = {}

    class Collection:
        def __init__(self, name: str) -> None:
            self.name = name

        def __str__(self) -> str:
            call_count[self.name] = call_count.get(self.name, 0) + 1
            return self.name

    city = make_city()
    c1 = Collection('Одна')
    c2 = Collection('Две')
    dto = make_city_details_dto(city=city, collections=[c1, c2])
    _ = dto.page_description

    assert call_count == {'Одна': 1, 'Две': 1}


# Тесты для некоторых других полей — просто проверить, что можно создавать DTO и поля доступны
def test_fields_are_set_correctly() -> None:
    city = make_city()
    dto = make_city_details_dto(
        city=city,
        average_rating=4.0,
        popular_months=['Март'],
        visits=[{'user': 'A', 'date': '2023-01-01'}],
        collections=[],
        number_of_visits=10,
        number_of_visits_all_users=100,
        number_of_users_who_visit_city=20,
        number_of_cities_in_country=500,
        number_of_cities_in_region=50,
        rank_in_country_by_visits=5,
        rank_in_country_by_users=7,
        rank_in_region_by_visits=3,
        rank_in_region_by_users=4,
        neighboring_cities_by_rank_in_country_by_visits=[city],
        neighboring_cities_by_rank_in_country_by_users=[city],
        neighboring_cities_by_rank_in_region_by_visits=[city],
        neighboring_cities_by_rank_in_region_by_users=[city],
    )

    assert dto.number_of_visits == 10
    assert dto.visits[0]['user'] == 'A'
    assert dto.average_rating == 4.0
    assert dto.popular_months == ['Март']
    assert dto.neighboring_cities_by_rank_in_country_by_visits == [city]


# Проверка, что page_title корректно работает с пустой строкой в регионе
def test_page_title_region_empty_string() -> None:
    city = make_city(region='')
    dto = make_city_details_dto(city=city)
    assert dto.page_title == 'Москва, Россия - информация о городе, карта'


# Проверка, что page_description корректно работает с пустыми коллекциями
def test_page_description_empty_collections() -> None:
    city = make_city()
    dto = make_city_details_dto(city=city, collections=[])
    desc = dto.page_description
    assert 'Входит в коллекцию' not in desc
    assert 'Входит в коллекции' not in desc


# Проверка, что page_description не ломается, если популярные месяцы None (должен быть пустой список)
def test_page_description_popular_months_none() -> None:
    city = make_city()
    dto = make_city_details_dto(city=city, popular_months=None)
    desc = dto.page_description
    assert 'Лучшее время для поездки' not in desc
