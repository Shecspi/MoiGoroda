"""
Интеграционные тесты для views приложения country.
"""

from typing import Any

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.integration
class TestCountryView:
    """Тесты для представления country."""

    @pytest.fixture
    def client(self) -> Client:
        """Возвращает тестовый клиент."""
        return Client()

    def test_view_accessible(self, client: Client) -> None:
        """Проверяет что представление доступно."""
        response = client.get(reverse('country_map'))

        assert response.status_code == 200

    def test_view_uses_correct_template(self, client: Client) -> None:
        """Проверяет что используется правильный шаблон."""
        response = client.get(reverse('country_map'))

        assert 'country/map.html' in [t.name for t in response.templates]

    def test_context_contains_page_title(self, client: Client) -> None:
        """Проверяет что контекст содержит page_title."""
        response = client.get(reverse('country_map'))

        assert 'page_title' in response.context
        assert response.context['page_title'] == 'Карта стран мира'

    def test_context_contains_page_description(self, client: Client) -> None:
        """Проверяет что контекст содержит page_description."""
        response = client.get(reverse('country_map'))

        assert 'page_description' in response.context
        assert response.context['page_description'] == 'Карта стран мира'

    def test_view_accessible_for_anonymous(self, client: Client) -> None:
        """Проверяет что представление доступно для анонимных пользователей."""
        response = client.get(reverse('country_map'))

        assert response.status_code == 200

    def test_view_accessible_for_authenticated(self, client: Client, user: User) -> None:
        """Проверяет что представление доступно для авторизованных пользователей."""
        client.force_login(user)
        response = client.get(reverse('country_map'))

        assert response.status_code == 200

