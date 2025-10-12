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

from city.models import VisitedCity, City
from region.models import Region, RegionType
from country.models import Country


# ===== Integration тесты для Dashboard View =====


@pytest.fixture
def setup_dashboard_data(django_user_model: Any) -> dict[str, Any]:
    """Фикстура для подготовки данных dashboard"""
    # Создаем суперюзера
    superuser = django_user_model.objects.create_superuser(
        username='admin', email='admin@test.com', password='adminpass'
    )

    # Создаем обычных пользователей
    user1 = django_user_model.objects.create_user(
        username='user1', email='user1@test.com', password='pass123'
    )
    user2 = django_user_model.objects.create_user(
        username='user2', email='user2@test.com', password='pass123'
    )

    # Создаем страну, тип региона, регион и город
    country = Country.objects.create(name='Россия', code='RU')
    region_type = RegionType.objects.create(title='Город')
    region = Region.objects.create(
        title='Москва', country=country, type=region_type, iso3166='RU-MOW-INT'
    )
    city = City.objects.create(
        title='Москва',
        region=region,
        country=country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )

    # Создаем посещенные города
    vc1 = VisitedCity.objects.create(
        user=user1, city=city, date_of_visit=date.today(), rating=5, has_magnet=True
    )
    vc2 = VisitedCity.objects.create(
        user=user2, city=city, date_of_visit=date.today(), rating=4, has_magnet=False
    )

    return {
        'superuser': superuser,
        'user1': user1,
        'user2': user2,
        'country': country,
        'region': region,
        'city': city,
        'vc1': vc1,
        'vc2': vc2,
    }


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_requires_authentication(client: Client) -> None:
    """Тест что dashboard требует авторизации"""
    response = client.get(reverse('dashboard'))

    assert response.status_code == 302
    # LoginRequiredMixin редиректит на LOGIN_URL (который установлен как '/')
    assert str(response.url) == '/'  # type: ignore[attr-defined]


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_redirects_non_superuser(client: Client, django_user_model: Any) -> None:
    """Тест что dashboard редиректит обычного пользователя"""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    client.force_login(user)

    response = client.get(reverse('dashboard'))

    assert response.status_code == 302
    assert str(response.url) == reverse('main_page')  # type: ignore[attr-defined]


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_allows_superuser(client: Client, setup_dashboard_data: dict[str, Any]) -> None:
    """Тест что dashboard доступен для суперюзера"""
    superuser = setup_dashboard_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('dashboard'))

    assert response.status_code == 200
    assert 'dashboard/dashboard.html' in [t.name for t in response.templates]


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_context_contains_user_statistics(
    client: Client, setup_dashboard_data: dict[str, Any]
) -> None:
    """Тест что контекст dashboard содержит статистику по пользователям"""
    superuser = setup_dashboard_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('dashboard'))

    assert 'qty_users' in response.context
    assert 'qty_registrations_yesteday' in response.context
    assert 'qty_registrations_week' in response.context
    assert 'qty_registrations_month' in response.context
    assert 'registrations_by_day' in response.context

    # Проверяем что количество пользователей правильное (3: superuser + 2 обычных)
    assert response.context['qty_users'] == 3


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_context_contains_city_statistics(
    client: Client, setup_dashboard_data: dict[str, Any]
) -> None:
    """Тест что контекст dashboard содержит статистику по городам"""
    superuser = setup_dashboard_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('dashboard'))

    assert 'qty_visited_cities' in response.context
    assert 'average_cities' in response.context
    assert 'qty_visited_cities_by_user' in response.context
    assert 'qty_user_without_visited_cities' in response.context

    # Проверяем количество посещенных городов (2 записи)
    assert response.context['qty_visited_cities'] == 2


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_calculates_average_cities_correctly(
    client: Client, setup_dashboard_data: dict[str, Any]
) -> None:
    """Тест правильности расчета среднего количества городов"""
    superuser = setup_dashboard_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('dashboard'))

    qty_visited_cities = response.context['qty_visited_cities']
    qty_users = response.context['qty_users']
    average_cities = response.context['average_cities']

    # Среднее = количество посещений / количество пользователей
    assert average_cities == int(qty_visited_cities / qty_users)


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_registrations_by_day_is_queryset(
    client: Client, setup_dashboard_data: dict[str, Any]
) -> None:
    """Тест что registrations_by_day является QuerySet"""
    superuser = setup_dashboard_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('dashboard'))

    registrations_by_day = response.context['registrations_by_day']
    assert hasattr(registrations_by_day, '__iter__')


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_qty_user_without_visited_cities(
    client: Client, setup_dashboard_data: dict[str, Any]
) -> None:
    """Тест расчета количества пользователей без посещенных городов"""
    superuser = setup_dashboard_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('dashboard'))

    # У нас 3 пользователя, из них 2 с посещенными городами
    # Значит 1 пользователь (superuser) без посещенных городов
    assert response.context['qty_user_without_visited_cities'] == 1


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_page_title_and_description(
    client: Client, setup_dashboard_data: dict[str, Any]
) -> None:
    """Тест что page_title и page_description установлены"""
    superuser = setup_dashboard_data['superuser']
    client.force_login(superuser)

    response = client.get(reverse('dashboard'))

    assert response.context['page_title'] == 'Dashboard'
    assert 'page_description' in response.context


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_with_no_users_except_superuser(client: Client, django_user_model: Any) -> None:
    """Тест dashboard когда нет обычных пользователей"""
    superuser = django_user_model.objects.create_superuser(
        username='admin', email='admin@test.com', password='adminpass'
    )
    client.force_login(superuser)

    response = client.get(reverse('dashboard'))

    assert response.status_code == 200
    assert response.context['qty_users'] == 1
    assert response.context['qty_visited_cities'] == 0
    assert response.context['qty_user_without_visited_cities'] == 1


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_with_many_users(client: Client, django_user_model: Any) -> None:
    """Тест dashboard с множеством пользователей"""
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')

    # Создаем 10 пользователей
    for i in range(10):
        django_user_model.objects.create_user(username=f'user{i}', password='pass')

    client.force_login(superuser)

    response = client.get(reverse('dashboard'))

    assert response.status_code == 200
    assert response.context['qty_users'] == 11  # 10 + 1 superuser


@pytest.mark.integration
@pytest.mark.django_db
def test_dashboard_registrations_yesterday_count(client: Client, django_user_model: Any) -> None:
    """Тест подсчета регистраций за вчера"""
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')

    # Создаем пользователя "вчера"
    yesterday_user = django_user_model.objects.create_user(
        username='yesterday_user', password='pass'
    )
    yesterday_user.date_joined = date.today() - timedelta(days=1)
    yesterday_user.save()

    client.force_login(superuser)

    response = client.get(reverse('dashboard'))

    assert response.status_code == 200
    # В контексте должна быть информация о регистрациях
    assert 'qty_registrations_yesteday' in response.context
