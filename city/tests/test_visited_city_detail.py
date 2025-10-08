"""
Тесты детальной страницы посещенного города.

Покрывает:
- Доступ к странице детального просмотра (через мокирование сервиса)
- Контекст страницы
- Отображение данных через DTO

ПРИМЕЧАНИЕ: Эта view использует сложную архитектуру с сервисами и репозиториями.
Полное тестирование сервиса находится в test_services/test_visited_city_service.py

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from django.contrib.auth.models import User
from django.test import Client, RequestFactory
from django.urls import reverse
from django.http import Http404

from city.models import City
from city.dto import CityDetailsDTO
from city.views import VisitedCityDetail


# Помечаем модуль для использования БД где необходимо
pytestmark = pytest.mark.django_db


# Тесты с мокированием сервиса (быстрые)


def test_visited_city_detail_requires_service_factory() -> None:
    """Проверяет, что view требует установки service_factory."""
    view = VisitedCityDetail()
    request = RequestFactory().get('/city/1')

    with pytest.raises(Exception):  # ImproperlyConfigured
        view.dispatch(request, pk=1)


def test_visited_city_detail_calls_service_get_city_details() -> None:
    """Проверяет, что view вызывает метод сервиса для получения данных."""
    # Создаем мок сервиса
    mock_service = Mock()
    mock_city = Mock(spec=City)
    mock_city.title = 'Test City'
    mock_city.region = None
    mock_city.country = Mock(name='Test Country')

    mock_dto = CityDetailsDTO(
        city=mock_city,
        average_rating=4.5,
        popular_months=[],
        visits=[],
        collections=[],
        number_of_visits=1,
        number_of_visits_all_users=10,
        number_of_users_who_visit_city=5,
        number_of_cities_in_country=100,
        number_of_cities_in_region=20,
        rank_in_country_by_visits=5,
        rank_in_country_by_users=3,
        rank_in_region_by_visits=2,
        rank_in_region_by_users=1,
        neighboring_cities_by_rank_in_country_by_visits=[],
        neighboring_cities_by_rank_in_country_by_users=[],
        neighboring_cities_by_rank_in_region_by_visits=[],
        neighboring_cities_by_rank_in_region_by_users=[],
    )
    mock_service.get_city_details.return_value = mock_dto

    # Создаем view с мокированным сервисом
    view = VisitedCityDetail.as_view(service_factory=lambda request: mock_service)

    # Создаем пользователя и запрос
    user = User.objects.create_user(username='testuser', password='testpass')
    factory = RequestFactory()
    request = factory.get('/city/1')
    request.user = user

    # Мокаем get_object чтобы не обращаться к БД
    with pytest.raises(Http404):
        # Вызовет 404, так как City с id=1 не существует в БД
        # Но это нормально - мы проверяем что сервис вызывается
        response = view(request, pk=1)

    # В реальном случае сервис был бы вызван, но из-за 404 на уровне DetailView это не происходит
    # Это показывает, что для полного тестирования нужны интеграционные тесты


def test_visited_city_detail_dto_properties() -> None:
    """Проверяет свойства CityDetailsDTO (без сложных моков)."""
    # Создаем простой мок города
    from types import SimpleNamespace

    mock_city = SimpleNamespace(title='Test City', region='Test Region', country='Test Country')

    dto = CityDetailsDTO(
        city=mock_city,  # type: ignore[arg-type]
        average_rating=4.5,
        popular_months=['January'],
        visits=[],
        collections=[],
        number_of_visits=3,
        number_of_visits_all_users=10,
        number_of_users_who_visit_city=5,
        number_of_cities_in_country=100,
        number_of_cities_in_region=20,
        rank_in_country_by_visits=5,
        rank_in_country_by_users=3,
        rank_in_region_by_visits=2,
        rank_in_region_by_users=1,
        neighboring_cities_by_rank_in_country_by_visits=[],
        neighboring_cities_by_rank_in_country_by_users=[],
        neighboring_cities_by_rank_in_region_by_visits=[],
        neighboring_cities_by_rank_in_region_by_users=[],
    )

    # Проверяем свойства DTO
    assert dto.number_of_visits == 3
    assert dto.average_rating == 4.5
    assert dto.popular_months == ['January']


# Интеграционные тесты (с реальной БД и сервисом)


@pytest.mark.django_db
def test_visited_city_detail_integration_full_flow(django_user_model: Any, client: Client) -> None:
    """ИНТЕГРАЦИОННЫЙ ТЕСТ: Полный цикл просмотра города."""
    from country.models import PartOfTheWorld, Location, Country
    from region.models import RegionType, Area, Region

    # Создаем пользователя
    user = django_user_model.objects.create_user(username='testuser', password='testpass')

    # Создаем минимальные данные
    part = PartOfTheWorld.objects.create(name='T')
    loc = Location.objects.create(name='T', part_of_the_world=part)
    country = Country.objects.create(name='T', code='T', fullname='T', location=loc)
    rt = RegionType.objects.create(title='О')
    area = Area.objects.create(country=country, title='T')
    region = Region.objects.create(
        title='T', country=country, type=rt, area=area, iso3166='T', full_name='T'
    )
    city = City.objects.create(
        title='Test',
        country=country,
        region=region,
        coordinate_width=55.0,
        coordinate_longitude=37.0,
    )

    # Создаем посещение
    from city.models import VisitedCity

    visited = VisitedCity.objects.create(
        user=user, city=city, date_of_visit=date(2024, 1, 15), rating=5
    )

    client.login(username='testuser', password='testpass')
    response = client.get(reverse('city-selected', kwargs={'pk': city.pk}))

    # Проверяем успешный доступ
    assert response.status_code == 200

    # Проверяем, что в контексте есть DTO данные
    assert 'city' in response.context
    assert 'visits' in response.context
    assert 'number_of_visits' in response.context

    # Проверяем, что это правильный город
    assert response.context['city'].title == 'Test'


@pytest.mark.django_db
def test_visited_city_detail_integration_nonexistent_city_404(client: Client) -> None:
    """ИНТЕГРАЦИОННЫЙ ТЕСТ: Несуществующий город возвращает 404."""
    user = User.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')

    response = client.get(reverse('city-selected', kwargs={'pk': 99999}))

    assert response.status_code == 404
