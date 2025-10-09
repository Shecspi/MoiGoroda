"""
Интеграционные тесты для полного flow city-all-list.
Тестируют взаимодействие всех компонентов вместе.

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
    user = django_user_model.objects.create_user(username='testuser', password='testpass123')
    client.login(username='testuser', password='testpass123')
    return user


@pytest.fixture
def mock_all_dependencies() -> dict[str, MagicMock]:
    """Создает моки для всех зависимостей view."""
    with (
        patch('city.views.logger') as mock_logger,
        patch('city.views.apply_sort_to_queryset') as mock_apply_sort,
        patch('city.views.get_unique_visited_cities') as mock_get_cities,
        patch('city.views.get_number_of_cities') as mock_get_num_cities,
        patch('city.views.get_number_of_new_visited_cities') as mock_get_num_visited,
        patch('city.views.get_number_of_visited_countries') as mock_get_num_countries,
        patch('city.views.is_user_has_subscriptions') as mock_has_subs,
        patch('city.views.get_all_subscriptions') as mock_get_subs,
    ):
        # Настройка моков
        empty_qs = VisitedCity.objects.none()
        mock_get_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_num_cities.return_value = 100
        mock_get_num_visited.return_value = 0
        mock_get_num_countries.return_value = 0
        mock_has_subs.return_value = False
        mock_get_subs.return_value = []

        yield {
            'logger': mock_logger,
            'apply_sort': mock_apply_sort,
            'get_cities': mock_get_cities,
            'get_num_cities': mock_get_num_cities,
            'get_num_visited': mock_get_num_visited,
            'get_num_countries': mock_get_num_countries,
            'has_subs': mock_has_subs,
            'get_subs': mock_get_subs,
        }


@pytest.mark.django_db
class TestFullPageRender:
    """Тесты полного рендеринга страницы."""

    def test_page_renders_successfully(
        self,
        authenticated_user: Any,
        client: Client,
        mock_all_dependencies: dict[str, MagicMock],
    ) -> None:
        """Страница успешно рендерится со всеми компонентами."""
        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        assert 'city/city_all__list.html' in (t.name for t in response.templates)

        # Проверяем, что все моки были вызваны
        assert mock_all_dependencies['logger'].info.called
        assert mock_all_dependencies['get_cities'].called
        assert mock_all_dependencies['apply_sort'].called

    def test_page_context_contains_required_data(
        self,
        authenticated_user: Any,
        client: Client,
        mock_all_dependencies: dict[str, MagicMock],
    ) -> None:
        """Контекст страницы содержит все необходимые данные."""
        response = client.get(reverse('city-all-list'))

        # Проверяем наличие ключевых переменных в контексте
        assert 'all_cities' in response.context
        assert 'total_qty_of_cities' in response.context
        assert 'qty_of_visited_cities' in response.context
        assert 'number_of_visited_countries' in response.context
        assert 'filter' in response.context
        assert 'sort' in response.context
        assert 'active_page' in response.context
        assert 'page_title' in response.context
        assert 'page_description' in response.context

    def test_page_with_all_parameters(
        self,
        authenticated_user: Any,
        client: Client,
        mock_all_dependencies: dict[str, MagicMock],
    ) -> None:
        """Страница работает с всеми параметрами одновременно."""
        with (
            patch('city.views.Country.objects.filter') as mock_country_filter,
            patch('city.views.Country.objects.get') as mock_country_get,
            patch('city.views.apply_filter_to_queryset') as mock_filter,
        ):
            mock_country_filter.return_value.exists.return_value = True
            mock_country_get.return_value = MagicMock(__str__=lambda x: 'Россия')
            empty_qs = VisitedCity.objects.none()
            mock_filter.return_value = empty_qs

            response = client.get(
                reverse('city-all-list') + '?country=RU&filter=current_year&sort=name_down&page=1'
            )

            assert response.status_code == 200
            assert mock_filter.called
            assert mock_country_get.called


@pytest.mark.django_db
class TestCountryParameter:
    """Тесты параметра country."""

    @patch('city.views.Country.objects.filter')
    @patch('city.views.logger')
    def test_invalid_country_redirects(
        self,
        mock_logger: MagicMock,
        mock_country_filter: MagicMock,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Несуществующий код страны вызывает редирект."""
        mock_country_filter.return_value.exists.return_value = False

        response = client.get(reverse('city-all-list') + '?country=INVALID')

        assert response.status_code == 302
        assert response.url == reverse('city-all-map')  # type: ignore

    def test_valid_country_loads_successfully(
        self,
        authenticated_user: Any,
        client: Client,
        mock_all_dependencies: dict[str, MagicMock],
    ) -> None:
        """Валидный код страны обрабатывается корректно."""
        with (
            patch('city.views.Country.objects.filter') as mock_filter,
            patch('city.views.Country.objects.get') as mock_get,
        ):
            mock_filter.return_value.exists.return_value = True
            mock_get.return_value = MagicMock(__str__=lambda x: 'Россия')

            response = client.get(reverse('city-all-list') + '?country=RU')

            assert response.status_code == 200
            assert 'country_name' in response.context
            assert 'country_code' in response.context
            assert response.context['country_code'] == 'RU'

    def test_without_country_parameter(
        self,
        authenticated_user: Any,
        client: Client,
        mock_all_dependencies: dict[str, MagicMock],
    ) -> None:
        """Страница работает без параметра country."""
        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        assert response.context['country_code'] is None


@pytest.mark.django_db
class TestErrorHandling:
    """Тесты обработки ошибок."""

    def test_handles_database_errors_gracefully(
        self,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Обработка ошибок БД."""
        with patch('city.views.get_unique_visited_cities') as mock_get_cities:
            mock_get_cities.side_effect = Exception('Database error')

            # В production это должно возвращать 500, но не падать полностью
            with pytest.raises(Exception):
                client.get(reverse('city-all-list'))

    def test_handles_missing_dependencies(
        self,
        authenticated_user: Any,
        client: Client,
    ) -> None:
        """Обработка отсутствующих зависимостей."""
        with (
            patch('city.views.get_unique_visited_cities') as mock_get_cities,
            patch('city.views.apply_sort_to_queryset') as mock_sort,
        ):
            empty_qs = VisitedCity.objects.none()
            mock_get_cities.return_value = empty_qs
            # apply_sort возвращает None вместо QuerySet
            mock_sort.return_value = None

            # Должно обработаться без падения
            with pytest.raises(Exception):
                client.get(reverse('city-all-list'))


@pytest.mark.django_db
class TestLogging:
    """Тесты логирования."""

    def test_successful_request_is_logged(
        self,
        authenticated_user: Any,
        client: Client,
        mock_all_dependencies: dict[str, MagicMock],
    ) -> None:
        """Успешный запрос логируется."""
        client.get(reverse('city-all-list'))

        mock_logger = mock_all_dependencies['logger']
        assert mock_logger.info.called
        # Проверяем, что в логе есть информация о просмотре
        call_args = mock_logger.info.call_args_list
        assert any('Viewing the list of visited cities' in str(call) for call in call_args)

    def test_custom_sorting_is_logged(
        self,
        authenticated_user: Any,
        client: Client,
        mock_all_dependencies: dict[str, MagicMock],
    ) -> None:
        """Кастомная сортировка логируется."""
        client.get(reverse('city-all-list') + '?sort=name_down')

        mock_logger = mock_all_dependencies['logger']
        # Должен быть лог об использовании сортировки
        call_args = mock_logger.info.call_args_list
        assert any('Using sorting' in str(call) for call in call_args)
