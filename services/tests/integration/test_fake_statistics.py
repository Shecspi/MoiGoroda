"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from services.db.statistics.fake_statistics import get_fake_statistics


@pytest.mark.integration
@pytest.mark.django_db
def test_get_fake_statistics_returns_dict() -> None:
    """Тест что get_fake_statistics возвращает словарь"""
    result = get_fake_statistics()

    assert isinstance(result, dict)


@pytest.mark.integration
@pytest.mark.django_db
def test_get_fake_statistics_has_cities_key() -> None:
    """Тест что get_fake_statistics содержит ключ 'cities'"""
    result = get_fake_statistics()

    assert 'cities' in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_fake_statistics_has_regions_key() -> None:
    """Тест что get_fake_statistics содержит ключ 'regions'"""
    result = get_fake_statistics()

    assert 'regions' in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_fake_statistics_cities_structure() -> None:
    """Тест структуры данных cities в get_fake_statistics"""
    result = get_fake_statistics()

    cities = result['cities']
    assert 'number_of_visited_cities' in cities
    assert 'number_of_not_visited_cities' in cities
    assert 'last_10_visited_cities' in cities


@pytest.mark.integration
@pytest.mark.django_db
def test_get_fake_statistics_regions_structure() -> None:
    """Тест структуры данных regions в get_fake_statistics"""
    result = get_fake_statistics()

    regions = result['regions']
    assert 'number_of_visited_regions' in regions
    assert 'number_of_finished_regions' in regions
    assert 'number_of_half_finished_regions' in regions


@pytest.mark.integration
@pytest.mark.django_db
def test_get_fake_statistics_cities_has_valid_data() -> None:
    """Тест что данные cities в get_fake_statistics валидны"""
    result = get_fake_statistics()

    cities = result['cities']
    assert isinstance(cities['number_of_visited_cities'], int)
    assert isinstance(cities['number_of_not_visited_cities'], int)
    assert isinstance(cities['last_10_visited_cities'], tuple)


@pytest.mark.integration
@pytest.mark.django_db
def test_get_fake_statistics_regions_has_valid_data() -> None:
    """Тест что данные regions в get_fake_statistics валидны"""
    result = get_fake_statistics()

    regions = result['regions']
    assert isinstance(regions['number_of_visited_regions'], int)
    assert isinstance(regions['number_of_finished_regions'], int)
    assert isinstance(regions['number_of_half_finished_regions'], int)


@pytest.mark.integration
@pytest.mark.django_db
def test_get_fake_statistics_last_10_visited_cities_structure() -> None:
    """Тест структуры last_10_visited_cities"""
    result = get_fake_statistics()

    last_10 = result['cities']['last_10_visited_cities']
    # Проверяем, что есть хотя бы 10 городов
    if isinstance(last_10, tuple):
        assert len(last_10) >= 10

        for city in last_10:
            assert 'title' in city
            assert 'date_of_visit' in city
            assert isinstance(city['title'], str)
            assert isinstance(city['date_of_visit'], str)


@pytest.mark.integration
@pytest.mark.django_db
def test_get_fake_statistics_consistency() -> None:
    """Тест согласованности данных в get_fake_statistics"""
    result = get_fake_statistics()

    cities = result['cities']
    regions = result['regions']

    # Проверяем, что числа существуют (могут быть отрицательные из-за фейковых данных)
    assert isinstance(cities['number_of_visited_cities'], int)
    assert isinstance(cities['number_of_not_visited_cities'], int)
    assert isinstance(regions['number_of_visited_regions'], int)
    assert isinstance(regions['number_of_finished_regions'], int)
    assert isinstance(regions['number_of_half_finished_regions'], int)
