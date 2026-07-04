# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""
Тесты контента и данных контекста страницы списка городов.
Проверяет корректность передаваемых данных, а не HTML разметку.
"""

from datetime import date
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.test import Client
from django.urls import reverse

from city.models import City, VisitedCity
from country.models import Country


@pytest.fixture
def authenticated_user(client: Client, django_user_model: Any) -> Any:
    """Создает и аутентифицирует пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass123')
    client.login(username='testuser', password='testpass123')
    return user


def create_mock_visited_city(
    city_id: int,
    title: str,
    region_title: str = 'Регион 1',
    date_of_visit: str | None = None,
    rating: int = 3,
    population: int | None = None,
    date_of_foundation: str | None = None,
) -> Mock:
    """Создает мок объекта VisitedCity."""
    mock_city = Mock()
    mock_city.id = city_id
    mock_city.title = title
    mock_city.region = Mock(title=region_title)
    mock_city.population = population
    mock_city.date_of_foundation = date_of_foundation

    mock_visited = Mock()
    mock_visited.id = city_id
    mock_visited.city = mock_city
    mock_visited.date_of_visit = date_of_visit
    mock_visited.rating = rating

    return mock_visited


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
class TestPageRender:
    """Тесты успешного рендеринга страницы."""

    def test_page_renders_with_correct_template(
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
        """Страница рендерится с правильным шаблоном."""
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
        assert 'city/list/page.html' in (t.name for t in response.templates)

    def test_page_renders_with_base_template(
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
        """Страница использует базовый шаблон."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        # Проверяем, что используется базовый шаблон
        template_names = [t.name for t in response.templates]
        assert 'base.html' in template_names or 'base-simple.html' in template_names


@pytest.mark.django_db
@pytest.mark.integration
class TestCityTimeline:
    """Тесты хронологии посещённых городов на странице списка городов."""

    def test_authenticated_user_sees_only_visited_city_timeline_with_expected_order(
        self,
        client: Client,
        django_user_model: Any,
    ) -> None:
        """Хронология показывает только посещения с датами по убыванию и даты без указания внизу."""
        user = django_user_model.objects.create_user(username='timeline-user', password='pass123')
        country = Country.objects.create(name='Россия', code='RU')
        visited_city = City.objects.create(
            title='Посещённый город',
            country=country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )
        undated_city = City.objects.create(
            title='Город без даты',
            country=country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )
        unvisited_city = City.objects.create(
            title='Непосещённый город',
            country=country,
            coordinate_width=57.0,
            coordinate_longitude=39.0,
        )

        VisitedCity.objects.create(
            user=user, city=visited_city, date_of_visit=date(2024, 5, 2), rating=5
        )
        VisitedCity.objects.create(
            user=user, city=visited_city, date_of_visit=date(2024, 1, 1), rating=4
        )
        VisitedCity.objects.create(user=user, city=undated_city, date_of_visit=None, rating=3)

        client.force_login(user)
        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        timeline_items = response.context['city_timeline_items']
        assert [item['city_title'] for item in timeline_items] == [
            visited_city.title,
            visited_city.title,
            undated_city.title,
        ]
        assert [item['date_label'] for item in timeline_items] == [
            '02.05.2024',
            '01.01.2024',
            'Без даты',
        ]
        assert [item['status'] for item in timeline_items] == ['visited', 'visited', 'visited']

        content = response.content.decode()
        assert unvisited_city.title not in content
        assert 'id="city-timeline-modal"' in content
        assert 'dui-modal' in content
        assert 'dui-timeline dui-timeline-vertical' in content
        assert 'data-timeline-modal-trigger="city-timeline-modal"' in content
        assert 'data-timeline-scroll-container' in content
        assert 'data-timeline-first-visited' in content
        assert 'Хронология' in content


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
class TestToolbarData:
    """Тесты данных для панели инструментов (проверка контекста, а не HTML)."""

    def test_statistics_display(
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
        """Статистика передается в контекст корректно."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 4
        mock_get_number_of_new_visited_cities.return_value = 3
        mock_get_number_of_visited_countries.return_value = 1
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        # Проверяем статистику в контексте
        assert response.context['total_qty_of_cities'] == 4
        assert response.context['qty_of_visited_cities'] == 3
        assert response.context['number_of_visited_countries'] == 1

    def test_map_button_context(
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
        """Данные для кнопки карты передаются в контекст."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        # Проверяем, что контекст содержит необходимые данные
        assert 'all_cities' in response.context

    def test_filter_data_in_context(
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
        """Данные фильтра передаются в контекст."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert 'filter' in response.context

    def test_sort_data_in_context(
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
        """Данные сортировки передаются в контекст."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert 'sort' in response.context
        assert response.context['sort'] == 'last_visit_date_down'


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
class TestEmptyState:
    """Тесты пустого состояния (когда нет городов)."""

    def test_empty_queryset_in_context(
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
        """При отсутствии городов в контексте пустой queryset."""
        mock_get_unique_visited_cities.return_value = []
        mock_apply_sort.return_value = []
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.status_code == 200
        assert len(response.context['object_list']) == 0
        assert response.context['qty_of_visited_cities'] == 0


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
class TestContextData:
    """Тесты контекстных данных."""

    def test_context_contains_all_required_fields(
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
        """Контекст содержит все необходимые поля."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 5
        mock_get_number_of_visited_countries.return_value = 2
        mock_is_user_has_subscriptions.return_value = True
        mock_get_all_subscriptions.return_value = [Mock(), Mock()]

        response = client.get(reverse('city-all-list'))

        required_fields = [
            'all_cities',
            'total_qty_of_cities',
            'qty_of_visited_cities',
            'number_of_visited_countries',
            'filter',
            'sort',
            'active_page',
            'is_user_has_subscriptions',
            'subscriptions',
            'has_advanced_premium',
            'page_title',
            'page_description',
            'country_name',
            'country_code',
        ]

        for field in required_fields:
            assert field in response.context, f"Field '{field}' missing in context"

    def test_statistics_values_correct(
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
        """Статистические значения передаются корректно."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 150
        mock_get_number_of_new_visited_cities.return_value = 42
        mock_get_number_of_visited_countries.return_value = 5
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.context['total_qty_of_cities'] == 150
        assert response.context['qty_of_visited_cities'] == 42
        assert response.context['number_of_visited_countries'] == 5

    def test_active_page_marker(
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
        """Маркер активной страницы установлен корректно."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.context['active_page'] == 'city_list'

    def test_subscriptions_data_included(
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
        """Данные о подписках включены в контекст."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0

        mock_subscriptions = [Mock(id=1), Mock(id=2), Mock(id=3)]
        mock_is_user_has_subscriptions.return_value = True
        mock_get_all_subscriptions.return_value = mock_subscriptions

        response = client.get(reverse('city-all-list'))

        assert response.context['is_user_has_subscriptions'] is True
        assert response.context['subscriptions'] == mock_subscriptions
        assert len(response.context['subscriptions']) == 3


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
class TestPageTitles:
    """Тесты заголовков страницы."""

    def test_default_page_title(
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
        """Заголовок по умолчанию отображается корректно."""
        empty_qs = VisitedCity.objects.none()
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        response = client.get(reverse('city-all-list'))

        assert response.context['page_title'] == 'Список посещённых городов'
        assert (
            response.context['page_description']
            == 'Список всех посещённых городов, отсортированный в порядке посещения'
        )

    @patch('city.views.Country.objects.filter')
    @patch('city.views.Country.objects.get')
    @patch('city.views.to_prepositional')
    def test_country_specific_page_title(
        self,
        mock_to_prepositional: MagicMock,
        mock_country_get: MagicMock,
        mock_country_filter: MagicMock,
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
        """Заголовок для конкретной страны формируется корректно."""
        empty_qs = VisitedCity.objects.none()
        mock_country_filter.return_value.exists.return_value = True
        mock_get_unique_visited_cities.return_value = empty_qs
        mock_apply_sort.return_value = empty_qs
        mock_get_number_of_cities.return_value = 100
        mock_get_number_of_new_visited_cities.return_value = 0
        mock_get_number_of_visited_countries.return_value = 0
        mock_is_user_has_subscriptions.return_value = False
        mock_get_all_subscriptions.return_value = []

        mock_country_get.return_value = Mock(__str__=lambda x: 'Россия')
        mock_to_prepositional.return_value = 'России'

        response = client.get(reverse('city-all-list') + '?country=RU')

        assert 'Список посещённых городов в России' in response.context['page_title']
        mock_to_prepositional.assert_called_once_with('Россия')
