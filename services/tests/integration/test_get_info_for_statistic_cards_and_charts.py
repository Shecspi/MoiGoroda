"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from services.db.statistics.get_info_for_statistic_cards_and_charts import (
    get_info_for_statistic_cards_and_charts,
)


@pytest.mark.integration
@pytest.mark.django_db
def test_get_info_for_statistic_cards_and_charts_returns_dict(django_user_model: Any) -> None:
    """Тест что get_info_for_statistic_cards_and_charts возвращает словарь"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_info_for_statistic_cards_and_charts(user.id)

    assert isinstance(result, dict)


@pytest.mark.integration
@pytest.mark.django_db
def test_get_info_for_statistic_cards_and_charts_has_cities_key(django_user_model: Any) -> None:
    """Тест что get_info_for_statistic_cards_and_charts содержит ключ 'cities'"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_info_for_statistic_cards_and_charts(user.id)

    assert 'cities' in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_info_for_statistic_cards_and_charts_has_regions_key(django_user_model: Any) -> None:
    """Тест что get_info_for_statistic_cards_and_charts содержит ключ 'regions'"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_info_for_statistic_cards_and_charts(user.id)

    assert 'regions' in result


@pytest.mark.integration
@pytest.mark.django_db
def test_get_info_for_statistic_cards_and_charts_cities_structure(django_user_model: Any) -> None:
    """Тест структуры данных cities"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_info_for_statistic_cards_and_charts(user.id)

    cities = result['cities']
    assert 'number_of_visited_cities' in cities
    assert 'number_of_new_visited_cities' in cities
    assert 'last_10_visited_cities' in cities


@pytest.mark.integration
@pytest.mark.django_db
def test_get_info_for_statistic_cards_and_charts_regions_structure(django_user_model: Any) -> None:
    """Тест структуры данных regions"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_info_for_statistic_cards_and_charts(user.id)

    regions = result['regions']
    assert 'number_of_visited_regions' in regions
    assert 'number_of_finished_regions' in regions


@pytest.mark.integration
@pytest.mark.django_db
def test_get_info_for_statistic_cards_and_charts_cities_has_valid_data(
    django_user_model: Any,
) -> None:
    """Тест что данные cities валидны"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_info_for_statistic_cards_and_charts(user.id)

    cities = result['cities']
    assert isinstance(cities['number_of_visited_cities'], int)
    assert isinstance(cities['number_of_new_visited_cities'], int)
    # last_10_visited_cities может быть list, tuple или QuerySet
    assert hasattr(cities['last_10_visited_cities'], '__iter__')


@pytest.mark.integration
@pytest.mark.django_db
def test_get_info_for_statistic_cards_and_charts_regions_has_valid_data(
    django_user_model: Any,
) -> None:
    """Тест что данные regions валидны"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_info_for_statistic_cards_and_charts(user.id)

    regions = result['regions']
    assert isinstance(regions['number_of_visited_regions'], int)
    assert isinstance(regions['number_of_finished_regions'], int)


@pytest.mark.integration
@pytest.mark.django_db
def test_get_info_for_statistic_cards_and_charts_consistency(django_user_model: Any) -> None:
    """Тест согласованности данных"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')

    result = get_info_for_statistic_cards_and_charts(user.id)

    cities = result['cities']
    regions = result['regions']

    # Проверяем, что числа не отрицательные
    assert cities['number_of_visited_cities'] >= 0
    assert cities['number_of_new_visited_cities'] >= 0
    assert regions['number_of_visited_regions'] >= 0
    assert regions['number_of_finished_regions'] >= 0
