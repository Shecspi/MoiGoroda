"""
Интеграционные тесты для полного flow city-all-map.
Тестируют взаимодействие всех компонентов вместе.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any, Generator
from unittest.mock import patch, MagicMock, Mock

import pytest
from django.test import Client
from django.urls import reverse


@pytest.fixture
def authenticated_user(client: Client, django_user_model: Any) -> Any:
    """Создает и аутентифицирует пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass123')
    client.login(username='testuser', password='testpass123')
    return user


@pytest.fixture
def mock_all_dependencies() -> Generator[dict[str, MagicMock], None, None]:
    """Создает моки для всех зависимостей view."""
    with (
        patch('city.views.logger') as mock_logger,
        patch('city.views.get_number_of_cities') as mock_get_num_cities,
        patch('city.views.get_number_of_new_visited_cities') as mock_get_num_visited,
        patch('city.views.get_number_of_visited_countries') as mock_get_num_countries,
        patch('city.views.is_user_has_subscriptions') as mock_has_subs,
        patch('city.views.get_all_subscriptions') as mock_get_subs,
    ):
        # Настройка моков
        mock_get_num_cities.return_value = 100
        mock_get_num_visited.return_value = 0
        mock_get_num_countries.return_value = 0
        mock_has_subs.return_value = False
        mock_get_subs.return_value = []

        yield {
            'logger': mock_logger,
            'get_num_cities': mock_get_num_cities,
            'get_num_visited': mock_get_num_visited,
            'get_num_countries': mock_get_num_countries,
            'has_subs': mock_has_subs,
            'get_subs': mock_get_subs,
        }


@pytest.mark.django_db
@pytest.mark.e2e
class TestFullPageRender:
    """Тесты полного рендеринга страницы карты."""

    def test_page_renders_successfully(
        self,
        authenticated_user: Any,
        client: Client,
        mock_all_dependencies: dict[str, MagicMock],
    ) -> None:
        """Страница карты успешно рендерится."""
        response = client.get(reverse('city-all-map'))

        assert response.status_code == 200
        assert 'city/city_all__map.html' in (t.name for t in response.templates)

        # Проверяем, что все моки были вызваны
        assert mock_all_dependencies['logger'].info.called
        assert mock_all_dependencies['get_num_cities'].called
        assert mock_all_dependencies['get_num_visited'].called

    def test_page_uses_base_template(
        self,
        authenticated_user: Any,
        client: Client,
        mock_all_dependencies: dict[str, MagicMock],
    ) -> None:
        """Страница использует базовый шаблон."""
        response = client.get(reverse('city-all-map'))

        template_names = [t.name for t in response.templates]
        assert 'base.html' in template_names or 'base-simple.html' in template_names

    def test_page_context_contains_required_data(
        self,
        authenticated_user: Any,
        client: Client,
        mock_all_dependencies: dict[str, MagicMock],
    ) -> None:
        """Контекст страницы содержит все необходимые данные."""
        response = client.get(reverse('city-all-map'))

        # Проверяем наличие ключевых переменных в контексте
        required_fields = [
            'total_qty_of_cities',
            'qty_of_visited_cities',
            'number_of_cities_in_country',
            'number_of_visited_cities_in_country',
            'number_of_visited_countries',
            'is_user_has_subscriptions',
            'subscriptions',
            'country_name',
            'country_code',
            'active_page',
            'page_title',
            'page_description',
        ]

        for field in required_fields:
            assert field in response.context, f"Field '{field}' missing in context"


@pytest.mark.django_db
@pytest.mark.e2e
class TestLogging:
    """Тесты логирования."""

    @patch('city.views.logger')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_map_view_is_logged(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Просмотр карты логируется."""
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 5
        mock_get_number_of_visited_countries.return_value = 2
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        client.get(reverse('city-all-map'))

        # Проверяем, что событие залогировано
        mock_logger.info.assert_called()
        call_args = str(mock_logger.info.call_args)
        assert 'Viewing the map of visited cities' in call_args


@pytest.mark.django_db
@pytest.mark.e2e
class TestErrorHandling:
    """Тесты обработки ошибок."""

    def test_handles_database_errors_gracefully(
        self,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Обработка ошибок БД."""
        with patch('city.views.get_number_of_cities') as mock_get_cities:
            mock_get_cities.side_effect = Exception('Database error')

            with pytest.raises(Exception):
                client.get(reverse('city-all-map'))

    @patch('city.views.logger')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_handles_missing_subscriptions_data(
        self,
        mock_get_all_subscriptions: MagicMock,
        mock_is_user_has_subscriptions: MagicMock,
        mock_get_number_of_visited_countries: MagicMock,
        mock_get_number_of_new_visited_cities: MagicMock,
        mock_get_number_of_cities: MagicMock,
        mock_logger: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Обработка отсутствия данных о подписках."""
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        # Возвращаем None вместо списка
        mock_is_user_has_subscriptions.return_value = None
        mock_get_all_subscriptions.return_value = None

        response = client.get(reverse('city-all-map'))

        # Должна быть корректная обработка
        assert response.status_code == 200
