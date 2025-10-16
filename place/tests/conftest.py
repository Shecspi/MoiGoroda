"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any


# Общие фикстуры для всех тестов приложения place


@pytest.fixture
def api_client() -> Any:
    """Фикстура для API клиента"""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def sample_tag() -> dict[str, str]:
    """Фикстура с тестовыми данными для тега"""
    return {'name': 'amenity'}


@pytest.fixture
def sample_category() -> dict[str, Any]:
    """Фикстура с тестовыми данными для категории"""
    return {
        'name': 'Кафе',
    }


@pytest.fixture
def sample_place() -> dict[str, Any]:
    """Фикстура с тестовыми данными для места"""
    return {
        'name': 'Кафе "Уютное"',
        'latitude': 55.7558,
        'longitude': 37.6173,
    }


@pytest.fixture
def sample_place_data() -> dict[str, Any]:
    """Фикстура с полными данными для создания места"""
    return {
        'name': 'Музей истории',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'category': None,  # Будет установлено в тестах
    }
