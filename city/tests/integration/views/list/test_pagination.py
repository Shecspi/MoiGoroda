"""
Тесты пагинации для страницы списка городов.
Проверяет корректность работы разбиения на страницы.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any
from unittest.mock import patch, MagicMock, Mock

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


def create_mock_visited_cities(count: int) -> list[Mock]:
    """Создает список моков VisitedCity."""
    cities = []
    for i in range(1, count + 1):
        mock_city = Mock()
        mock_city.id = i
        mock_city.city = Mock(
            id=i,
            title=f'Город {i}',
            region=Mock(title='Регион 1'),
            population=None,
            date_of_foundation=None,
        )
        mock_city.date_of_visit = None
        mock_city.rating = 3
        cities.append(mock_city)
    return cities


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
class TestPagination:
    """Тесты пагинации."""

    def test_no_pagination_for_few_items(
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
        """Пагинация не отображается для маленького количества элементов (< 24)."""
        # Создаем 10 городов (меньше чем paginate_by=24)
        mock_cities = create_mock_visited_cities(10)

        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = mock_cities
        mock_apply_sort.return_value = mock_cities
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 10
        mock_get_number_of_visited_countries.return_value = 1
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        # Проверяем, что пагинация не нужна
        assert 'is_paginated' in response.context
        assert response.context['is_paginated'] is False

    def test_pagination_appears_for_many_items(
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
        """Пагинация отображается для большого количества элементов (> 24)."""
        # Создаем 60 городов (больше чем paginate_by=24)
        mock_cities = create_mock_visited_cities(60)

        mock_get_unique_visited_cities.return_value = mock_cities
        mock_apply_sort.return_value = mock_cities
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 60
        mock_get_number_of_visited_countries.return_value = 1
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert 'is_paginated' in response.context
        assert response.context['is_paginated'] is True
        assert response.context['paginator'].num_pages == 3

    def test_first_page_buttons(
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
        """На первой странице кнопки prev/first неактивны."""
        mock_cities = create_mock_visited_cities(60)

        mock_get_unique_visited_cities.return_value = mock_cities
        mock_apply_sort.return_value = mock_cities
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 60
        mock_get_number_of_visited_countries.return_value = 1
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))
        page_obj = response.context['page_obj']

        assert page_obj.number == 1
        assert not page_obj.has_previous()
        assert page_obj.has_next()

    def test_middle_page_buttons(
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
        """На средней странице все кнопки активны."""
        mock_cities = create_mock_visited_cities(60)

        mock_get_unique_visited_cities.return_value = mock_cities
        mock_apply_sort.return_value = mock_cities
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 60
        mock_get_number_of_visited_countries.return_value = 1
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list') + '?page=2')
        page_obj = response.context['page_obj']

        assert page_obj.number == 2
        assert page_obj.has_previous()
        assert page_obj.has_next()

    def test_last_page_buttons(
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
        """На последней странице кнопки next/last неактивны."""
        mock_cities = create_mock_visited_cities(60)

        mock_get_unique_visited_cities.return_value = mock_cities
        mock_apply_sort.return_value = mock_cities
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 60
        mock_get_number_of_visited_countries.return_value = 1
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list') + '?page=3')
        page_obj = response.context['page_obj']

        assert page_obj.number == 3
        assert page_obj.has_previous()
        assert not page_obj.has_next()

    def test_invalid_page_number(
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
        """Некорректный номер страницы обрабатывается."""
        mock_cities = create_mock_visited_cities(60)

        mock_get_unique_visited_cities.return_value = mock_cities
        mock_apply_sort.return_value = mock_cities
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 60
        mock_get_number_of_visited_countries.return_value = 1
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        # Запрашиваем несуществующую страницу
        response = client.get(reverse('city-all-list') + '?page=999')

        # Django должен вернуть последнюю страницу или 404
        assert response.status_code in [200, 404]

    def test_non_numeric_page_parameter(
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
        """Нечисловой параметр page обрабатывается."""
        mock_cities = create_mock_visited_cities(60)

        mock_get_unique_visited_cities.return_value = mock_cities
        mock_apply_sort.return_value = mock_cities
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 60
        mock_get_number_of_visited_countries.return_value = 1
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list') + '?page=abc')

        # Должна вернуться первая страница
        assert response.status_code == 404

    def test_pagination_persists_other_parameters(
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
        """Пагинация сохраняет другие параметры (filter, sort)."""
        with (
            patch('city.views.Country.objects.filter') as mock_country_filter,
            patch('city.views.Country.objects.get') as mock_country_get,
            patch('city.views.apply_filter_to_queryset') as mock_filter,
        ):
            mock_cities = create_mock_visited_cities(60)

            mock_country_filter.return_value.exists.return_value = True
            mock_get_unique_visited_cities.return_value = mock_cities
            mock_filter.return_value = mock_cities
            mock_apply_sort.return_value = mock_cities
            mock_get_number_of_cities.return_value = 100
            mock_get_number_of_new_visited_cities.return_value = 60
            mock_get_number_of_visited_countries.return_value = 1
            mock_is_user_has_subscriptions.return_value = False
            mock_get_all_subscriptions.return_value = []
            mock_country_get.return_value = Mock(__str__=lambda x: 'Россия')

            response = client.get(
                reverse('city-all-list') + '?page=2&filter=current_year&sort=name_down&country=RU'
            )

            assert response.status_code == 200
            assert response.context['filter'] == 'current_year'
            assert response.context['sort'] == 'name_down'
            assert response.context['country_code'] == 'RU'


@pytest.mark.django_db
@pytest.mark.integration
class TestPaginationEdgeCases:
    """Тесты граничных случаев пагинации."""

    @patch('city.views.logger')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_exactly_one_page_of_items(
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
        """Ровно 24 элемента (одна страница)."""
        mock_cities = create_mock_visited_cities(24)

        mock_get_unique_visited_cities.return_value = mock_cities
        mock_apply_sort.return_value = mock_cities
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 24
        mock_get_number_of_visited_countries.return_value = 1
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.context['is_paginated'] is False
        assert len(response.context['page_obj']) == 24

    @patch('city.views.logger')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_one_item_more_than_page_size(
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
        """25 элементов (на 1 больше чем страница) - появляется пагинация."""
        mock_cities = create_mock_visited_cities(25)

        mock_get_unique_visited_cities.return_value = mock_cities
        mock_apply_sort.return_value = mock_cities
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 25
        mock_get_number_of_visited_countries.return_value = 1
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.context['is_paginated'] is True
        assert response.context['paginator'].num_pages == 2
        assert len(response.context['page_obj']) == 24

    @patch('city.views.logger')
    @patch('city.views.apply_sort_to_queryset')
    @patch('city.views.get_unique_visited_cities')
    @patch('city.views.get_number_of_cities')
    @patch('city.views.get_number_of_new_visited_cities')
    @patch('city.views.get_number_of_visited_countries')
    @patch('city.views.is_user_has_subscriptions')
    @patch('city.views.get_all_subscriptions')
    def test_empty_results(
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
        """Пустой результат отображается корректно."""
        mock_get_unique_visited_cities.return_value = []
        mock_apply_sort.return_value = []
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        assert response.context['is_paginated'] is False
