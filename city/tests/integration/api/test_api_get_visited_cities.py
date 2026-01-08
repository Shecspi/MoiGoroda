"""
Тесты для API GetVisitedCities.

Покрывает:
- Аутентификацию и права доступа
- HTTP методы (разрешенные и запрещенные)
- Получение списка посещённых городов
- Фильтрацию по стране
- Применение различных фильтров
- Логирование

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date, datetime
from typing import Type
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

VISITED_CITIES_URL = reverse('api__get_visited_cities')


# Fixtures


@pytest.fixture
def api_client() -> APIClient:
    """Создает APIClient для тестирования."""
    return APIClient()


@pytest.fixture
def authenticated_user(api_client: APIClient, django_user_model: Type[User]) -> User:
    """Создает аутентифицированного пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def superuser(api_client: APIClient, django_user_model: Type[User]) -> User:
    """Создает суперпользователя."""
    admin = django_user_model.objects.create_superuser(username='admin', password='admin')
    api_client.force_authenticate(user=admin)
    return admin


# Тесты доступа и методов


@pytest.mark.integration
def test_get_visited_cities_guest_cannot_access(api_client: APIClient) -> None:
    """Проверяет, что гость не может получить доступ к API."""
    response = api_client.get(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
@pytest.mark.integration
def test_get_visited_cities_prohibited_methods(
    api_client: APIClient, authenticated_user: User, method: str
) -> None:
    """Проверяет, что запрещенные методы возвращают 405."""
    client_method = getattr(api_client, method)
    response = client_method(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.integration
def test_get_visited_cities_superuser_can_access(api_client: APIClient, superuser: User) -> None:
    """Проверяет, что суперпользователь может получить доступ к API."""
    with patch('city.api.GetVisitedCities.get_queryset', return_value=[]):
        response = api_client.get(VISITED_CITIES_URL)
        assert response.status_code == status.HTTP_200_OK


# Тесты получения данных


@patch('city.api.get_unique_visited_cities')
@pytest.mark.integration
def test_get_visited_cities_authenticated_user_gets_list(
    mock_get_unique_visited_cities: MagicMock, api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет успешное получение списка посещённых городов."""
    # Создаем мок VisitedCity
    mock_city = MagicMock()
    mock_city.user.username = 'testuser'
    mock_city.city.id = 42
    mock_city.city.title = 'Mock City'
    mock_city.city.region = 'Mock Region'
    mock_city.city.region_id = 7
    mock_city.city.coordinate_width = '55.7558'
    mock_city.city.coordinate_longitude = '37.6173'
    from datetime import date

    mock_city.date_of_visit = datetime(2024, 1, 15)
    mock_city.number_of_visits = 3
    mock_city.first_visit_date = '2022-06-01'
    mock_city.last_visit_date = '2024-01-15'
    mock_city.visit_dates = [date(2024, 1, 15)]  # Добавляем visit_dates для сериализатора
    mock_city.average_rating = 4.5

    mock_queryset = MagicMock()
    mock_queryset.__iter__.return_value = [mock_city]
    mock_get_unique_visited_cities.return_value = mock_queryset

    response = api_client.get(VISITED_CITIES_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['title'] == 'Mock City'
    assert data[0]['username'] == 'testuser'
    assert data[0]['id'] == 42
    assert data[0]['region_title'] == 'Mock Region'
    assert data[0]['region_id'] == 7
    assert data[0]['lat'] == '55.7558'
    assert data[0]['lon'] == '37.6173'
    assert data[0]['number_of_visits'] == 3
    assert data[0]['first_visit_date'] == '2022-06-01'
    assert data[0]['visit_years'] == [2024]
    assert data[0]['average_rating'] == 4.5


@patch('city.api.GetVisitedCities.get_queryset')
@pytest.mark.integration
def test_get_visited_cities_empty_list(
    mock_get_queryset: MagicMock, api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет, что API возвращает пустой список, если городов нет."""
    mock_get_queryset.return_value = []
    response = api_client.get(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@patch('city.api.get_unique_visited_cities')
@pytest.mark.integration
def test_get_visited_cities_multiple_cities(
    mock_get_unique_visited_cities: MagicMock, api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет возврат нескольких посещённых городов."""
    mock_city_1 = MagicMock()
    mock_city_1.user.username = 'testuser'
    mock_city_1.city.id = 1
    mock_city_1.city.title = 'City One'
    mock_city_1.city.region = 'Region 1'
    mock_city_1.city.region_id = 1
    mock_city_1.city.coordinate_width = '10.0'
    mock_city_1.city.coordinate_longitude = '20.0'
    mock_city_1.date_of_visit = datetime(2020, 1, 1)
    mock_city_1.number_of_visits = 1
    mock_city_1.first_visit_date = '2020-01-01'
    mock_city_1.last_visit_date = '2020-01-01'
    mock_city_1.visit_dates = [date(2020, 1, 1)]  # Добавляем visit_dates для сериализатора
    mock_city_1.average_rating = 3.0

    mock_city_2 = MagicMock()
    mock_city_2.user.username = 'testuser'
    mock_city_2.city.id = 2
    mock_city_2.city.title = 'City Two'
    mock_city_2.city.region = 'Region 2'
    mock_city_2.city.region_id = 2
    mock_city_2.city.coordinate_width = '30.0'
    mock_city_2.city.coordinate_longitude = '40.0'
    mock_city_2.date_of_visit = datetime(2021, 6, 15)
    mock_city_2.number_of_visits = 2
    mock_city_2.first_visit_date = '2021-06-15'
    mock_city_2.last_visit_date = '2021-06-15'
    mock_city_2.visit_dates = [date(2021, 6, 15)]  # Добавляем visit_dates для сериализатора
    mock_city_2.average_rating = 4.0

    mock_get_unique_visited_cities.return_value = [mock_city_1, mock_city_2]

    response = api_client.get(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]['title'] == 'City One'
    assert data[1]['title'] == 'City Two'


# Тесты фильтрации


@patch('city.api.get_unique_visited_cities')
@pytest.mark.integration
def test_get_visited_cities_filter_by_country(
    mock_get_unique_visited_cities: MagicMock, api_client: APIClient, authenticated_user: User
) -> None:
    """Проверяет фильтрацию городов по стране."""
    mock_queryset = MagicMock()
    mock_queryset.__iter__.return_value = []
    mock_get_unique_visited_cities.return_value = mock_queryset

    response = api_client.get(VISITED_CITIES_URL, {'country': 'RU'})

    assert response.status_code == status.HTTP_200_OK
    # Проверяем, что функция была вызвана с правильными параметрами
    mock_get_unique_visited_cities.assert_called_once_with(authenticated_user.pk, 'RU')


@patch('city.api.apply_filter_to_queryset')
@patch('city.api.get_unique_visited_cities')
@pytest.mark.integration
def test_get_visited_cities_with_magnet_filter(
    mock_get_unique_visited_cities: MagicMock,
    mock_apply_filter: MagicMock,
    api_client: APIClient,
    authenticated_user: User,
) -> None:
    """Проверяет применение фильтра 'magnet' (города с сувенирами)."""
    mock_base_queryset = MagicMock()
    mock_filtered_queryset = MagicMock()
    mock_filtered_queryset.__iter__.return_value = []

    mock_get_unique_visited_cities.return_value = mock_base_queryset
    mock_apply_filter.return_value = mock_filtered_queryset

    response = api_client.get(VISITED_CITIES_URL, {'filter': 'magnet'})

    assert response.status_code == status.HTTP_200_OK
    mock_apply_filter.assert_called_once_with(mock_base_queryset, authenticated_user.pk, 'magnet')


@patch('city.api.apply_filter_to_queryset')
@patch('city.api.get_unique_visited_cities')
@pytest.mark.integration
def test_get_visited_cities_with_no_magnet_filter(
    mock_get_unique_visited_cities: MagicMock,
    mock_apply_filter: MagicMock,
    api_client: APIClient,
    authenticated_user: User,
) -> None:
    """Проверяет применение фильтра 'no_magnet' (города без сувениров)."""
    mock_base_queryset = MagicMock()
    mock_filtered_queryset = MagicMock()
    mock_filtered_queryset.__iter__.return_value = []

    mock_get_unique_visited_cities.return_value = mock_base_queryset
    mock_apply_filter.return_value = mock_filtered_queryset

    response = api_client.get(VISITED_CITIES_URL, {'filter': 'no_magnet'})

    assert response.status_code == status.HTTP_200_OK
    mock_apply_filter.assert_called_once_with(
        mock_base_queryset, authenticated_user.pk, 'no_magnet'
    )


@patch('city.api.apply_filter_to_queryset')
@patch('city.api.get_unique_visited_cities')
@pytest.mark.integration
def test_get_visited_cities_with_current_year_filter(
    mock_get_unique_visited_cities: MagicMock,
    mock_apply_filter: MagicMock,
    api_client: APIClient,
    authenticated_user: User,
) -> None:
    """Проверяет применение фильтра 'current_year' (города текущего года)."""
    mock_base_queryset = MagicMock()
    mock_filtered_queryset = MagicMock()
    mock_filtered_queryset.__iter__.return_value = []

    mock_get_unique_visited_cities.return_value = mock_base_queryset
    mock_apply_filter.return_value = mock_filtered_queryset

    response = api_client.get(VISITED_CITIES_URL, {'filter': 'current_year'})

    assert response.status_code == status.HTTP_200_OK
    mock_apply_filter.assert_called_once_with(
        mock_base_queryset, authenticated_user.pk, 'current_year'
    )


@patch('city.api.apply_filter_to_queryset')
@patch('city.api.get_unique_visited_cities')
@pytest.mark.integration
def test_get_visited_cities_with_last_year_filter(
    mock_get_unique_visited_cities: MagicMock,
    mock_apply_filter: MagicMock,
    api_client: APIClient,
    authenticated_user: User,
) -> None:
    """Проверяет применение фильтра 'last_year' (города прошлого года)."""
    mock_base_queryset = MagicMock()
    mock_filtered_queryset = MagicMock()
    mock_filtered_queryset.__iter__.return_value = []

    mock_get_unique_visited_cities.return_value = mock_base_queryset
    mock_apply_filter.return_value = mock_filtered_queryset

    response = api_client.get(VISITED_CITIES_URL, {'filter': 'last_year'})

    assert response.status_code == status.HTTP_200_OK
    mock_apply_filter.assert_called_once_with(
        mock_base_queryset, authenticated_user.pk, 'last_year'
    )


@patch('city.api.apply_filter_to_queryset')
@patch('city.api.get_unique_visited_cities')
@pytest.mark.integration
def test_get_visited_cities_with_country_and_filter(
    mock_get_unique_visited_cities: MagicMock,
    mock_apply_filter: MagicMock,
    api_client: APIClient,
    authenticated_user: User,
) -> None:
    """Проверяет одновременное применение фильтра по стране и дополнительного фильтра."""
    mock_base_queryset = MagicMock()
    mock_filtered_queryset = MagicMock()
    mock_filtered_queryset.__iter__.return_value = []

    mock_get_unique_visited_cities.return_value = mock_base_queryset
    mock_apply_filter.return_value = mock_filtered_queryset

    response = api_client.get(VISITED_CITIES_URL, {'country': 'US', 'filter': 'magnet'})

    assert response.status_code == status.HTTP_200_OK
    mock_get_unique_visited_cities.assert_called_once_with(authenticated_user.pk, 'US')
    mock_apply_filter.assert_called_once_with(mock_base_queryset, authenticated_user.pk, 'magnet')


# Тесты логирования


@patch('city.api.logger')
@patch('city.api.get_unique_visited_cities')
@pytest.mark.integration
def test_get_visited_cities_logs_successful_request(
    mock_get_unique_visited_cities: MagicMock,
    mock_logger: MagicMock,
    api_client: APIClient,
    authenticated_user: User,
) -> None:
    """Проверяет, что успешный запрос логируется."""
    mock_city = MagicMock()
    mock_city.user.username = 'testuser'
    mock_city.city.id = 1
    mock_city.city.title = 'Mock City'
    mock_city.city.region = 'Mock Region'
    mock_city.city.region_id = 1
    mock_city.city.coordinate_width = '10.0'
    mock_city.city.coordinate_longitude = '20.0'
    mock_city.date_of_visit = datetime(2024, 1, 1)
    mock_city.number_of_visits = 1
    mock_city.first_visit_date = '2024-01-01'
    mock_city.last_visit_date = '2024-01-01'
    mock_city.visit_dates = [date(2024, 1, 1)]  # Добавляем visit_dates для сериализатора
    mock_city.average_rating = 4.0

    mock_get_unique_visited_cities.return_value = [mock_city]

    response = api_client.get(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_200_OK

    mock_logger.info.assert_called_once()
    args, kwargs = mock_logger.info.call_args
    # Проверяем, что в логе есть ID пользователя
    assert 'user #' in args[1]
    assert str(authenticated_user.id) in args[1]


@pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
@patch('city.api.logger')
@patch('city.api.get_unique_visited_cities')
@pytest.mark.integration
def test_get_visited_cities_no_logging_on_prohibited_methods(
    mock_get_unique_visited_cities: MagicMock,
    mock_logger: MagicMock,
    api_client: APIClient,
    authenticated_user: User,
    method: str,
) -> None:
    """Проверяет, что запрещенные методы не логируются."""
    client_method = getattr(api_client, method)
    response = client_method(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    mock_logger.info.assert_not_called()
