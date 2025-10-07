"""
Общие фикстуры и утилиты для тестирования API эндпоинтов города.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date
from typing import Any, Type
from unittest.mock import MagicMock
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from city.models import City, VisitedCity


@pytest.fixture
def api_client() -> APIClient:
    """Фикстура для создания API клиента."""
    return APIClient()


@pytest.fixture
def authenticated_user(
    api_client: APIClient, django_user_model: Type[User]
) -> User:  # django_user_model - специальная фикстура pytest-django
    """Фикстура для создания авторизованного пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def superuser(
    api_client: APIClient, django_user_model: Type[User]
) -> User:  # django_user_model - специальная фикстура pytest-django
    """Фикстура для создания суперпользователя."""
    superuser = django_user_model.objects.create_superuser(username='admin', password='admin')
    api_client.force_authenticate(user=superuser)
    return superuser


@pytest.fixture
def mock_country() -> MagicMock:
    """Фикстура для создания мока страны."""
    return MagicMock(id=1, name='Russia', code='RU')


@pytest.fixture
def mock_region() -> MagicMock:
    """Фикстура для создания мока региона."""
    return MagicMock(id=1, title='Moscow Region', country_id=1)


@pytest.fixture
def mock_city(mock_country: MagicMock, mock_region: MagicMock) -> MagicMock:
    """Фикстура для создания мока города."""
    city = MagicMock(spec=City)
    city.id = 1
    city.title = 'Moscow'
    city.country = mock_country
    city.region = mock_region
    city.coordinate_width = 55.7558
    city.coordinate_longitude = 37.6173
    return city


@pytest.fixture
def mock_visited_city(mock_city: MagicMock) -> MagicMock:
    """Фикстура для создания мока посещенного города."""
    visited_city = MagicMock(spec=VisitedCity)
    visited_city.city = mock_city
    visited_city.user.username = 'testuser'
    visited_city.date_of_visit = date(2024, 1, 15)
    visited_city.rating = 5
    visited_city.has_magnet = True
    visited_city.impression = 'Great city!'
    visited_city.number_of_visits = 3
    visited_city.first_visit_date = '2022-06-01'
    visited_city.last_visit_date = '2024-01-15'
    visited_city.average_rating = 4.5
    visited_city.visit_years = [2022, 2023, 2024]
    # Добавляем атрибут visit_dates для сериализатора
    visited_city.visit_dates = [date(2022, 6, 1), date(2023, 8, 15), date(2024, 1, 15)]
    return visited_city
