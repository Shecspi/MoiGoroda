"""
Тесты прав доступа к странице списка городов.
Проверяет authentication и authorization.

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
    """Создает и аутентифицирует пользователя."""
    user = django_user_model.objects.create_user(
        username='testuser', password='testpass123', email='test@example.com'
    )
    client.login(username='testuser', password='testpass123')
    return user


@pytest.mark.django_db
@patch('city.views.logger')
@pytest.mark.integration
class TestGuestAccess:
    """Тесты доступа для неаутентифицированных пользователей."""

    def test_guest_redirected_to_login(
        self,
        mock_logger: MagicMock,
        client: Client,
    ) -> None:
        """Гость перенаправляется на страницу входа."""
        response = client.get(reverse('city-all-list'))

        assert response.status_code == 302
        assert response.url.startswith('/account/signin')  # type: ignore

    def test_guest_redirect_preserves_next_url(
        self,
        mock_logger: MagicMock,
        client: Client,
    ) -> None:
        """Редирект сохраняет URL для возврата после входа."""
        response = client.get(reverse('city-all-list'))

        assert 'next=/city/all/list' in response.url  # type: ignore

    def test_guest_cannot_access_with_params(
        self,
        mock_logger: MagicMock,
        client: Client,
    ) -> None:
        """Гость не может получить доступ даже с параметрами."""
        response = client.get(reverse('city-all-list') + '?country=RU&filter=current_year')

        assert response.status_code == 302
        assert response.url.startswith('/account/signin')  # type: ignore


@pytest.mark.django_db
@patch('city.views.logger')
@patch('city.views.apply_sort_to_queryset')
@patch('city.views.get_unique_visited_cities')
@patch('city.views.get_number_of_cities')
@patch('city.views.get_number_of_new_visited_cities')
@patch('city.views.get_number_of_visited_countries')
@patch('city.views.is_user_has_subscriptions')
@patch('city.views.get_all_subscriptions')
@pytest.mark.integration
class TestAuthenticatedAccess:
    """Тесты доступа для аутентифицированных пользователей."""

    def test_authenticated_user_has_access(
        self,
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
        """Аутентифицированный пользователь имеет доступ к странице."""
        # Настройка моков
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        assert 'city/city_all__list.html' in (t.name for t in response.templates)

    def test_different_users_see_their_own_data(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_get_unique_visited_cities: MagicMock,
        mock_apply_sort: MagicMock,
        mock_logger: MagicMock,
        client: Client,
        django_user_model: Any,
    ) -> None:
        """Разные пользователи видят свои данные."""
        # Создаем двух пользователей
        user1 = django_user_model.objects.create_user(username='user1', password='pass1')
        user2 = django_user_model.objects.create_user(username='user2', password='pass2')

        # Настройка моков
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Логинимся как user1
        client.login(username='user1', password='pass1')
        client.get(reverse('city-all-list'))

        # Проверяем, что get_unique_visited_cities вызван с ID user1
        call_args = mock_get_unique_visited_cities.call_args
        assert call_args[0][0] == user1.pk

        mock_get_unique_visited_cities.reset_mock()

        # Логинимся как user2
        client.logout()
        client.login(username='user2', password='pass2')
        client.get(reverse('city-all-list'))

        # Проверяем, что get_unique_visited_cities вызван с ID user2
        call_args = mock_get_unique_visited_cities.call_args
        assert call_args[0][0] == user2.pk

    def test_logout_revokes_access(
        self,
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
        """После выхода доступ отзывается."""
        # Настройка моков
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Сначала доступ есть
        response = client.get(reverse('city-all-list'))
        assert response.status_code == 200

        # После logout доступа нет
        client.logout()
        response = client.get(reverse('city-all-list'))
        assert response.status_code == 302
        assert response.url.startswith('/account/signin')  # type: ignore
