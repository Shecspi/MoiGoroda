"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from datetime import date, timedelta
from typing import Any

from django.test import Client
from django.urls import reverse
from rest_framework import status

from country.models import Country, PartOfTheWorld, Location, VisitedCountry


# ===== Integration тесты для Dashboard API =====


@pytest.fixture
def setup_api_data(django_user_model: Any) -> dict[str, Any]:
    """Фикстура для подготовки данных для API"""
    # Создаем суперюзера
    superuser = django_user_model.objects.create_superuser(
        username='admin', email='admin@test.com', password='adminpass'
    )

    # Создаем обычного пользователя
    user = django_user_model.objects.create_user(
        username='testuser', email='test@test.com', password='testpass'
    )

    # Создаем часть света и location
    part_of_world = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part_of_world)

    # Создаем страны
    country1 = Country.objects.create(name='Россия', code='RU', location=location)
    country2 = Country.objects.create(name='Германия', code='DE', location=location)

    # Создаем посещенные страны
    vc1 = VisitedCountry.objects.create(user=superuser, country=country1)
    vc2 = VisitedCountry.objects.create(user=superuser, country=country2)
    vc3 = VisitedCountry.objects.create(user=user, country=country1)

    return {
        'superuser': superuser,
        'user': user,
        'country1': country1,
        'country2': country2,
        'vc1': vc1,
        'vc2': vc2,
        'vc3': vc3,
    }


@pytest.mark.integration
@pytest.mark.django_db
def test_get_total_visited_countries_requires_authentication(client: Client) -> None:
    """Тест что API требует авторизации"""
    response = client.get(reverse('api__get_total_visited_countries'))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db
def test_get_total_visited_countries_requires_admin(client: Client, django_user_model: Any) -> None:
    """Тест что API требует прав администратора"""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    client.force_login(user)

    response = client.get(reverse('api__get_total_visited_countries'))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
@pytest.mark.django_db
def test_get_total_visited_countries_success(
    client: Client, setup_api_data: dict[str, Any]
) -> None:
    """Тест успешного получения общего количества посещенных стран"""
    superuser = setup_api_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('api__get_total_visited_countries'))

    assert response.status_code == status.HTTP_200_OK
    assert 'qty' in response.json()
    assert response.json()['qty'] == 3  # Всего 3 записи VisitedCountry


@pytest.mark.integration
@pytest.mark.django_db
def test_get_users_with_visited_countries_success(
    client: Client, setup_api_data: dict[str, Any]
) -> None:
    """Тест получения количества пользователей с посещенными странами"""
    superuser = setup_api_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('api__get_qty_users_with_visited_countries'))

    assert response.status_code == status.HTTP_200_OK
    assert 'qty' in response.json()
    assert response.json()['qty'] == 2  # 2 пользователя с посещенными странами


@pytest.mark.integration
@pytest.mark.django_db
def test_get_average_qty_visited_countries_success(
    client: Client, setup_api_data: dict[str, Any]
) -> None:
    """Тест получения среднего количества посещенных стран"""
    superuser = setup_api_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('api__get_average_qty_visited_countries'))

    assert response.status_code == status.HTTP_200_OK
    assert 'qty' in response.json()
    # 3 посещения / 2 пользователя = 1 (целочисленное деление)
    assert response.json()['qty'] == 1


@pytest.mark.integration
@pytest.mark.django_db
def test_get_max_qty_visited_countries_success(
    client: Client, setup_api_data: dict[str, Any]
) -> None:
    """Тест получения максимального количества посещенных стран"""
    superuser = setup_api_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('api__max_qty_visited_countries'))

    assert response.status_code == status.HTTP_200_OK
    assert 'qty' in response.json()
    # У superuser 2 страны, у user 1 страна, максимум = 2
    assert response.json()['qty'] == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_get_added_visited_countries_yesterday_success(
    client: Client, setup_api_data: dict[str, Any]
) -> None:
    """Тест получения количества добавленных стран за вчера (1 день)"""
    superuser = setup_api_data['superuser']
    client.force_login(superuser)

    url = reverse('api__get_qty_of_added_visited_countries', kwargs={'days': 1})
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert 'qty' in response.json()
    # Все страны добавлены сегодня, за вчера должно быть 0 или больше в зависимости от данных
    assert isinstance(response.json()['qty'], int)


@pytest.mark.integration
@pytest.mark.django_db
def test_get_added_visited_countries_week_success(
    client: Client, setup_api_data: dict[str, Any]
) -> None:
    """Тест получения количества добавленных стран за неделю (7 дней)"""
    superuser = setup_api_data['superuser']
    client.force_login(superuser)

    url = reverse('api__get_qty_of_added_visited_countries', kwargs={'days': 7})
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert 'qty' in response.json()
    assert isinstance(response.json()['qty'], int)


@pytest.mark.integration
@pytest.mark.django_db
def test_get_added_visited_countries_by_day_success(
    client: Client, setup_api_data: dict[str, Any]
) -> None:
    """Тест получения количества добавленных стран по дням"""
    superuser = setup_api_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('api__get_added_visited_countries_by_day'))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

    # Проверяем структуру данных
    if len(response.json()) > 0:
        first_item = response.json()[0]
        assert 'date' in first_item
        assert 'qty' in first_item


@pytest.mark.integration
@pytest.mark.django_db
def test_api_endpoints_with_different_days_parameters(
    client: Client, setup_api_data: dict[str, Any]
) -> None:
    """Тест API с разными значениями параметра days"""
    superuser = setup_api_data['superuser']
    client.force_login(superuser)

    days_values = [1, 7, 30, 365]

    for days in days_values:
        url = reverse('api__get_qty_of_added_visited_countries', kwargs={'days': days})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'qty' in response.json()


@pytest.mark.integration
@pytest.mark.django_db
def test_get_added_visited_countries_by_day_returns_max_50_items(
    client: Client, django_user_model: Any
) -> None:
    """Тест что API возвращает максимум 50 элементов"""
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    user = django_user_model.objects.create_user(username='user', password='pass')

    # Создаем часть света и location
    part_of_world = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part_of_world)

    # Создаем 60 стран и посещений в разные дни
    for i in range(60):
        # Код страны - 2 символа, используем A0-Z9 и комбинации
        code = f'{chr(65 + i // 10)}{i % 10}'
        country = Country.objects.create(name=f'Страна{i}', code=code, location=location)
        vc = VisitedCountry.objects.create(user=user, country=country)
        # Меняем дату добавления
        vc.added_at = date.today() - timedelta(days=i)
        vc.save()

    client.force_login(superuser)

    response = client.get(reverse('api__get_added_visited_countries_by_day'))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) <= 50


@pytest.mark.integration
@pytest.mark.django_db
def test_api_returns_zero_when_no_data(client: Client, django_user_model: Any) -> None:
    """Тест что API возвращает 0 когда нет данных"""
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    client.force_login(superuser)

    response = client.get(reverse('api__get_total_visited_countries'))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['qty'] == 0


@pytest.mark.integration
@pytest.mark.django_db
def test_get_average_qty_handles_zero_users(client: Client, django_user_model: Any) -> None:
    """Тест обработки деления на ноль когда нет пользователей с посещенными странами"""
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')

    # Создаем часть света, location и страну (но НЕ создаем посещенные страны)
    part_of_world = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part_of_world)
    _country = Country.objects.create(name='Россия', code='RU', location=location)

    client.force_login(superuser)

    # API должен обработать случай когда нет данных
    response = client.get(reverse('api__get_average_qty_visited_countries'))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['qty'] == 0
