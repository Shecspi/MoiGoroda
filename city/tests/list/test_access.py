"""
Тестирует доступность страницы для авторизованного и неавторизованного пользователей.
Страница тестирования '/city/all/list'.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any
from unittest.mock import patch, MagicMock

import pytest
from django.test import Client
from django.urls import reverse

from city.models import VisitedCity


@pytest.fixture
def authenticated_user(client: Client, django_user_model: Any) -> Any:
    """Создает и возвращает аутентифицированного пользователя."""
    user = django_user_model.objects.create_user(username='username', password='password')
    client.login(username='username', password='password')
    return user


@pytest.mark.django_db
@patch('city.views.logger')
def test_guest_redirected_to_login(mock_logger: MagicMock, client: Client) -> None:
    """Проверяет, что неаутентифицированный пользователь перенаправляется на страницу входа."""
    response = client.get(reverse('city-all-list'))

    assert response.status_code == 302
    assert response.url.startswith('/account/signin')  # type: ignore

    # Проверяем редирект с follow=True
    response = client.get(reverse('city-all-list'), follow=True)
    assert response.status_code == 200
    assert 'account/signin.html' in (t.name for t in response.templates)


@pytest.mark.django_db
@patch('city.views.logger')
@patch('city.views.apply_sort_to_queryset')
@patch('city.views.get_unique_visited_cities')
@patch('city.views.get_number_of_cities')
@patch('city.views.get_number_of_new_visited_cities')
@patch('city.views.get_number_of_visited_countries')
@patch('city.views.is_user_has_subscriptions')
@patch('city.views.get_all_subscriptions')
def test_authenticated_user_has_access(
    mock_get_all_subscriptions: MagicMock,
    mock_is_user_has_subscriptions: MagicMock,
    mock_get_number_of_visited_countries: MagicMock,
    mock_get_number_of_new_visited_cities: MagicMock,
    mock_get_number_of_cities: MagicMock,
    mock_get_unique_visited_cities: MagicMock,
    mock_apply_sort: MagicMock,
    mock_logger: MagicMock,
    authenticated_user: Any,
    client: Client,
) -> None:
    """Проверяет, что аутентифицированный пользователь имеет доступ к странице списка городов."""
    # Настройка моков - возвращаем пустой QuerySet
    empty_queryset = VisitedCity.objects.none()
    mock_get_unique_visited_cities.return_value = empty_queryset
    mock_apply_sort.return_value = empty_queryset  # Возвращаем тот же QuerySet без сортировки
    mock_get_number_of_cities.return_value = 100
    mock_get_number_of_new_visited_cities.return_value = 10
    mock_get_number_of_visited_countries.return_value = 3
    mock_is_user_has_subscriptions.return_value = False
    mock_get_all_subscriptions.return_value = []

    response = client.get(reverse('city-all-list'))

    assert response.status_code == 200
    assert 'city/city_all__list.html' in (t.name for t in response.templates)

    # Проверяем, что логгер был вызван
    mock_logger.info.assert_called()


@pytest.mark.django_db
@patch('city.views.logger')
@patch('city.views.Country.objects.filter')
def test_redirect_on_invalid_country_code(
    mock_country_filter: MagicMock,
    mock_logger: MagicMock,
    authenticated_user: Any,
    client: Client,
) -> None:
    """Проверяет редирект при передаче несуществующего кода страны."""
    # Настраиваем мок: страна не существует
    mock_country_filter.return_value.exists.return_value = False

    response = client.get(reverse('city-all-list') + '?country=INVALID')

    assert response.status_code == 302
    assert response.url == reverse('city-all-map')  # type: ignore
