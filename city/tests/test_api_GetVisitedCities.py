"""
----------------------------------------------

Copyright Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime

import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse


VISITED_CITIES_URL = reverse('api__get_visited_cities')


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_user(api_client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser', password='pass')
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def superuser(api_client, django_user_model):
    superuser = django_user_model.objects.create_superuser(username='admin', password='admin')
    api_client.force_authenticate(user=superuser)
    return superuser


def test_guest_cannot_access(api_client):
    response = api_client.get(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
def test_prohibited_methods(api_client, authenticated_user, method):
    client_method = getattr(api_client, method)
    response = client_method(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@patch('city.api.get_all_visited_cities')
def test_authenticated_user_gets_visited_cities(
    mock_get_all_visited_cities, api_client, authenticated_user
):
    # Полноценный мок VisitedCity
    mock_city_obj = MagicMock()
    mock_city_obj.user.username = 'testuser'
    mock_city_obj.city.id = 42
    mock_city_obj.city.title = 'Mock City'
    mock_city_obj.city.region = 'Mock Region'
    mock_city_obj.city.region_id = 7
    mock_city_obj.city.coordinate_width = '55.7558'
    mock_city_obj.city.coordinate_longitude = '37.6173'
    mock_city_obj.date_of_visit = datetime(2024, 1, 15)
    mock_city_obj.number_of_visits = 3
    mock_city_obj.date_of_first_visit = '2022-06-01'
    mock_city_obj.average_rating = 4.5

    mock_queryset = MagicMock()
    mock_queryset.__iter__.return_value = [mock_city_obj]
    mock_get_all_visited_cities.return_value = mock_queryset

    response = api_client.get(reverse('api__get_visited_cities'))

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert data[0]['title'] == 'Mock City'
    assert data[0]['username'] == 'testuser'
    assert data[0]['id'] == 42
    assert data[0]['region_title'] == 'Mock Region'
    assert data[0]['region_id'] == 7
    assert data[0]['lat'] == '55.7558'
    assert data[0]['lon'] == '37.6173'
    assert data[0]['year'] == 2024
    assert data[0]['number_of_visits'] == 3
    assert data[0]['date_of_first_visit'] == '2022-06-01'
    assert data[0]['average_rating'] == 4.5


@patch('city.api.GetVisitedCities.get_queryset')
def test_authenticated_user_receives_empty_list(mock_get_queryset, api_client, authenticated_user):
    mock_get_queryset.return_value = []
    response = api_client.get(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@patch('city.api.GetVisitedCities.get_queryset')
def test_superuser_can_access(mock_get_queryset, api_client, superuser):
    mock_get_queryset.return_value = []
    response = api_client.get(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_200_OK


@patch('city.api.get_all_visited_cities')
def test_multiple_visited_cities_returned(
    mock_get_all_visited_cities, api_client, authenticated_user
):
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
    mock_city_1.date_of_first_visit = '2020-01-01'
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
    mock_city_2.date_of_first_visit = '2021-06-15'
    mock_city_2.average_rating = 4.0

    mock_get_all_visited_cities.return_value = [mock_city_1, mock_city_2]

    response = api_client.get(VISITED_CITIES_URL)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['title'] == 'City One'
    assert data[1]['title'] == 'City Two'


@patch('city.api.logger')
@patch('city.api.get_all_visited_cities')
def test_logging_for_get_visited_cities(
    mock_get_all_visited_cities, mock_logger, api_client, authenticated_user
):
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
    mock_city.date_of_first_visit = '2024-01-01'
    mock_city.average_rating = 4.0

    mock_get_all_visited_cities.return_value = [mock_city]

    response = api_client.get(VISITED_CITIES_URL)
    assert response.status_code == 200

    mock_logger.info.assert_called_once()
    args, kwargs = mock_logger.info.call_args
    # Первый аргумент — self.request
    assert 'user #' in args[1]
    assert str(authenticated_user.id) in args[1]


@pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
@patch('city.api.logger')
@patch('city.api.get_all_visited_cities')
def test_logging_not_triggered_on_non_get_methods(
    mock_get_all_visited_cities, mock_logger, api_client, authenticated_user, method
):
    client_method = getattr(api_client, method)
    response = client_method(VISITED_CITIES_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    mock_logger.info.assert_not_called()
