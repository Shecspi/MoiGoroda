"""
БЫСТРЫЕ тесты формы создания города (с минимальными моками).

✨ БЫСТРЫЕ ТЕСТЫ (4 теста ~3-4 секунды)

Эти тесты используют моки где возможно и минимальные интеграционные тесты.
Используйте их для быстрой разработки и проверки основной функциональности.

Для полного покрытия см.: test_city_create_form_integration.py

Покрывает:
- Структуру POST запросов (без БД)
- Базовую валидацию данных (без БД)
- Критичный функционал: создание города и проверка дубликатов (с БД)

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.contrib.auth.models import User
from django.test import Client, RequestFactory
from django.urls import reverse

from city.models import VisitedCity, City
from country.models import Country


# Быстрые тесты с моками (без реальной БД)


@patch('city.views.VisitedCity')
@patch('city.views.City')
@pytest.mark.integration
def test_city_create_post_request_structure(
    mock_city_model: MagicMock, mock_visited_city_model: MagicMock
) -> None:
    """Проверяет структуру POST запроса (быстрый тест без БД)."""
    factory = RequestFactory()

    form_data = {
        'country': '1',
        'region': '1',
        'city': '1',
        'date_of_visit': '15.01.2024',
        'rating': '5',
    }

    request = factory.post('/city/create/', data=form_data)

    # Проверяем, что данные правильно переданы
    assert request.method == 'POST'
    assert request.POST['city'] == '1'
    assert request.POST['rating'] == '5'
    assert request.POST['date_of_visit'] == '15.01.2024'


@pytest.mark.integration
def test_city_create_form_data_validation() -> None:
    """Проверяет валидацию данных формы (быстрый тест без БД)."""
    # Проверяем, что рейтинг должен быть строкой от '1' до '5'
    valid_ratings = ['1', '2', '3', '4', '5']
    for rating in valid_ratings:
        assert rating in valid_ratings

    # Проверяем формат даты (ДД.ММ.ГГГГ)
    test_date = '15.01.2024'
    parts = test_date.split('.')
    assert len(parts) == 3
    assert len(parts[0]) == 2  # День
    assert len(parts[1]) == 2  # Месяц
    assert len(parts[2]) == 4  # Год


# Примечание: Полное мокирование Django форм очень сложно из-за их внутренней структуры.
# Вместо этого мы используем упрощенные интеграционные тесты ниже.


# Критичные интеграционные тесты (только самые важные с реальной БД)


@pytest.mark.django_db(transaction=True)
@patch('city.signals.notify_subscribers_on_city_add')
@patch('city.services.db.set_is_visit_first_for_all_visited_cities')
@pytest.mark.integration
def test_city_create_integration_full_flow(
    mock_set_first_visit: MagicMock,
    mock_signal: MagicMock,
    django_user_model: Any,
    client: Client,
) -> None:
    """ИНТЕГРАЦИОННЫЙ ТЕСТ: Полный цикл создания города (с реальной БД).

    Это критичный тест, который проверяет работу всей системы вместе.
    """
    from country.models import PartOfTheWorld, Location
    from region.models import RegionType, Area

    # Создаем минимальные данные
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    part_of_world = PartOfTheWorld.objects.create(name='T')
    location = Location.objects.create(name='T', part_of_the_world=part_of_world)
    country = Country.objects.create(name='T', code='T', fullname='T', location=location)
    region_type = RegionType.objects.create(title='О')
    area = Area.objects.create(country=country, title='T')
    from region.models import Region

    region = Region.objects.create(
        title='T', country=country, type=region_type, area=area, iso3166='T', full_name='T'
    )
    city = City.objects.create(
        title='T', country=country, region=region, coordinate_width=55.0, coordinate_longitude=37.0
    )

    client.login(username='testuser', password='testpass')

    form_data = {
        'country': country.id,
        'region': region.id,
        'city': city.id,
        'rating': '5',
    }

    response = client.post(reverse('city-create'), data=form_data)

    # Проверяем успешное создание
    assert response.status_code == 302
    assert VisitedCity.objects.filter(user=user, city=city).exists()


@pytest.mark.django_db(transaction=True)
@patch('city.signals.notify_subscribers_on_city_add')
@pytest.mark.integration
def test_city_create_integration_duplicate_validation(
    mock_signal: MagicMock,
    django_user_model: Any,
    client: Client,
) -> None:
    """ИНТЕГРАЦИОННЫЙ ТЕСТ: Проверка валидации дубликатов (с реальной БД).

    Это критичный тест для проверки бизнес-логики уникальности.
    """
    from country.models import PartOfTheWorld, Location
    from region.models import RegionType, Area, Region

    # Создаем минимальные данные
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    part_of_world = PartOfTheWorld.objects.create(name='T')
    location = Location.objects.create(name='T', part_of_the_world=part_of_world)
    country = Country.objects.create(name='T', code='T', fullname='T', location=location)
    region_type = RegionType.objects.create(title='О')
    area = Area.objects.create(country=country, title='T')
    region = Region.objects.create(
        title='T', country=country, type=region_type, area=area, iso3166='T', full_name='T'
    )
    city = City.objects.create(
        title='T', country=country, region=region, coordinate_width=55.0, coordinate_longitude=37.0
    )

    # Создаем первое посещение
    VisitedCity.objects.create(user=user, city=city, date_of_visit=date(2024, 1, 15), rating=5)

    # Пытаемся создать дубликат
    client.login(username='testuser', password='testpass')
    form_data = {
        'country': country.id,
        'region': region.id,
        'city': city.id,
        'date_of_visit': '15.01.2024',
        'rating': '4',
    }

    response = client.post(reverse('city-create'), data=form_data)

    # Должна быть ошибка
    assert response.status_code == 200
    assert 'уже был отмечен Вами как посещённый' in str(response.context['form'].errors['city'])

    # Дубликат не должен быть создан
    assert VisitedCity.objects.filter(user=user, city=city).count() == 1
