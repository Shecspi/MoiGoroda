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

from city.models import VisitedCity, City
from region.models import Region, RegionType
from country.models import Country, PartOfTheWorld, Location, VisitedCountry


# ===== E2E тесты для Dashboard =====


@pytest.fixture
def setup_full_dashboard_data(django_user_model: Any) -> dict[str, Any]:
    """Фикстура с полным набором данных для dashboard"""
    # Создаем суперюзера
    superuser = django_user_model.objects.create_superuser(
        username='admin', email='admin@test.com', password='adminpass'
    )

    # Создаем пользователей в разные дни
    users = []
    for i in range(5):
        user = django_user_model.objects.create_user(
            username=f'user{i}', email=f'user{i}@test.com', password='pass123'
        )
        # Распределяем регистрации по дням
        user.date_joined = date.today() - timedelta(days=i)
        user.save()
        users.append(user)

    # Создаем географические данные для городов
    country_city = Country.objects.create(name='Россия', code='RU')
    region_type = RegionType.objects.create(title='Город')
    region = Region.objects.create(
        title='Москва', country=country_city, type=region_type, iso3166='RU-MOW-E2E'
    )
    cities = []
    for i in range(3):
        city = City.objects.create(
            title=f'Город{i}',
            region=region,
            country=country_city,
            coordinate_width=55.0 + i,
            coordinate_longitude=37.0 + i,
        )
        cities.append(city)

    # Создаем посещенные города
    visited_cities = []
    for user in users[:3]:  # Только первые 3 пользователя
        for city in cities:
            vc = VisitedCity.objects.create(
                user=user, city=city, date_of_visit=date.today(), rating=5, has_magnet=True
            )
            visited_cities.append(vc)

    # Создаем данные для стран
    part_of_world = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part_of_world)

    countries = []
    for i in range(3):
        country = Country.objects.create(name=f'Страна{i}', code=f'X{i}', location=location)
        countries.append(country)

    # Создаем посещенные страны
    visited_countries_list = []
    for user in users[:2]:  # Только первые 2 пользователя
        for country in countries:
            vc_country = VisitedCountry.objects.create(user=user, country=country)
            visited_countries_list.append(vc_country)

    return {
        'superuser': superuser,
        'users': users,
        'cities': cities,
        'visited_cities': visited_cities,
        'countries': countries,
        'visited_countries': visited_countries_list,
    }


@pytest.mark.e2e
@pytest.mark.django_db
def test_full_dashboard_workflow_for_superuser(
    client: Client, setup_full_dashboard_data: dict[str, Any]
) -> None:
    """Полный сценарий работы с dashboard для суперюзера"""
    superuser = setup_full_dashboard_data['superuser']

    # Шаг 1: Пытаемся открыть dashboard без авторизации
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    # LoginRequiredMixin редиректит на LOGIN_URL (который установлен как '/')
    assert str(response.url) == '/'  # type: ignore[attr-defined]

    # Шаг 2: Авторизуемся как суперюзер
    client.force_login(superuser)

    # Шаг 3: Открываем dashboard
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200

    # Шаг 4: Проверяем что все данные отображаются
    assert response.context['qty_users'] == 6  # 5 users + 1 superuser
    assert response.context['qty_visited_cities'] == 9  # 3 users * 3 cities
    assert response.context['average_cities'] > 0

    # Шаг 5: Проверяем API endpoints
    api_urls = [
        'api__get_total_visited_countries',
        'api__get_qty_users_with_visited_countries',
        'api__get_average_qty_visited_countries',
        'api__max_qty_visited_countries',
    ]

    for url_name in api_urls:
        response = client.get(reverse(url_name))
        assert response.status_code == status.HTTP_200_OK
        assert 'qty' in response.json()

    # Шаг 6: Проверяем API с параметром days
    for days in [1, 7, 30, 365]:
        url = reverse('api__get_qty_of_added_visited_countries', kwargs={'days': days})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    # Шаг 7: Проверяем API для графика
    response = client.get(reverse('api__get_added_visited_countries_by_day'))
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.e2e
@pytest.mark.django_db
def test_regular_user_cannot_access_dashboard(client: Client, django_user_model: Any) -> None:
    """Сценарий попытки доступа к dashboard обычным пользователем"""
    # Шаг 1: Создаем обычного пользователя
    user = django_user_model.objects.create_user(username='regular_user', password='pass123')

    # Шаг 2: Авторизуемся
    client.force_login(user)

    # Шаг 3: Пытаемся открыть dashboard
    response = client.get(reverse('dashboard'))

    # Шаг 4: Проверяем редирект на главную
    assert response.status_code == 302
    assert str(response.url) == reverse('main_page')  # type: ignore[attr-defined]

    # Шаг 5: Пытаемся вызвать API
    response = client.get(reverse('api__get_total_visited_countries'))

    # Шаг 6: Проверяем что доступ запрещен
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.e2e
@pytest.mark.django_db
def test_dashboard_statistics_update_after_adding_data(
    client: Client, django_user_model: Any
) -> None:
    """Сценарий обновления статистики после добавления новых данных"""
    # Шаг 1: Создаем суперюзера
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    client.force_login(superuser)

    # Шаг 2: Открываем dashboard и сохраняем начальные значения
    response = client.get(reverse('dashboard'))
    initial_qty_users = response.context['qty_users']
    initial_qty_cities = response.context['qty_visited_cities']

    # Шаг 3: Добавляем нового пользователя
    new_user = django_user_model.objects.create_user(username='new_user', password='pass123')

    # Шаг 4: Снова открываем dashboard
    response = client.get(reverse('dashboard'))

    # Шаг 5: Проверяем что количество пользователей увеличилось
    assert response.context['qty_users'] == initial_qty_users + 1

    # Шаг 6: Добавляем посещенный город
    country = Country.objects.create(name='Россия', code='RU')
    region_type2 = RegionType.objects.create(title='Область')
    region = Region.objects.create(
        title='Москва', country=country, type=region_type2, iso3166='RU-MOW-E22'
    )
    city = City.objects.create(
        title='Москва',
        region=region,
        country=country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )
    VisitedCity.objects.create(
        user=new_user, city=city, date_of_visit=date.today(), rating=5, has_magnet=True
    )

    # Шаг 7: Снова открываем dashboard
    response = client.get(reverse('dashboard'))

    # Шаг 8: Проверяем что количество посещенных городов увеличилось
    assert response.context['qty_visited_cities'] == initial_qty_cities + 1


@pytest.mark.e2e
@pytest.mark.django_db
def test_dashboard_api_data_consistency(
    client: Client, setup_full_dashboard_data: dict[str, Any]
) -> None:
    """Сценарий проверки согласованности данных между view и API"""
    superuser = setup_full_dashboard_data['superuser']
    client.force_login(superuser)

    # Шаг 1: Получаем данные из view
    response = client.get(reverse('dashboard'))
    view_qty_visited_cities = response.context['qty_visited_cities']

    # Шаг 2: Получаем данные из API для стран
    response = client.get(reverse('api__get_total_visited_countries'))
    api_qty_visited_countries = response.json()['qty']

    # Шаг 3: Проверяем что данные корректны
    assert view_qty_visited_cities > 0
    assert api_qty_visited_countries > 0

    # Шаг 4: Получаем данные о пользователях
    response = client.get(reverse('api__get_qty_users_with_visited_countries'))
    api_qty_users = response.json()['qty']

    # Шаг 5: Проверяем что есть пользователи с посещенными странами
    assert api_qty_users > 0


@pytest.mark.e2e
@pytest.mark.django_db
def test_dashboard_handles_empty_data_gracefully(client: Client, django_user_model: Any) -> None:
    """Сценарий работы dashboard с пустыми данными"""
    # Шаг 1: Создаем только суперюзера, без других данных
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    client.force_login(superuser)

    # Шаг 2: Открываем dashboard
    response = client.get(reverse('dashboard'))

    # Шаг 3: Проверяем что страница открылась
    assert response.status_code == 200

    # Шаг 4: Проверяем что значения равны нулю или корректны
    assert response.context['qty_users'] == 1
    assert response.context['qty_visited_cities'] == 0
    assert response.context['average_cities'] == 0
    assert response.context['qty_user_without_visited_cities'] == 1

    # Шаг 5: Проверяем API endpoints
    api_response = client.get(reverse('api__get_total_visited_countries'))
    assert api_response.status_code == status.HTTP_200_OK
    assert api_response.json()['qty'] == 0


@pytest.mark.e2e
@pytest.mark.django_db
def test_dashboard_api_days_parameter_logic(client: Client, django_user_model: Any) -> None:
    """Сценарий проверки логики параметра days в API"""
    # Шаг 1: Создаем суперюзера
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')
    user = django_user_model.objects.create_user(username='user', password='pass')

    # Шаг 2: Создаем географические данные
    part_of_world = PartOfTheWorld.objects.create(name='Европа')
    location = Location.objects.create(name='Восточная Европа', part_of_the_world=part_of_world)

    # Шаг 3: Создаем посещенные страны в разные дни
    today_country = Country.objects.create(name='Сегодня', code='TD', location=location)
    VisitedCountry.objects.create(user=user, country=today_country)

    week_ago_country = Country.objects.create(name='Неделю назад', code='WK', location=location)
    vc_week = VisitedCountry.objects.create(user=user, country=week_ago_country)
    vc_week.added_at = date.today() - timedelta(days=7)
    vc_week.save()

    month_ago_country = Country.objects.create(name='Месяц назад', code='MN', location=location)
    vc_month = VisitedCountry.objects.create(user=user, country=month_ago_country)
    vc_month.added_at = date.today() - timedelta(days=30)
    vc_month.save()

    # Шаг 4: Авторизуемся
    client.force_login(superuser)

    # Шаг 5: Проверяем количество за 1 день (должна быть хотя бы сегодняшняя)
    response = client.get(reverse('api__get_qty_of_added_visited_countries', kwargs={'days': 1}))
    qty_1_day = response.json()['qty']

    # Шаг 6: Проверяем количество за 7 дней (должно быть >= qty_1_day)
    response = client.get(reverse('api__get_qty_of_added_visited_countries', kwargs={'days': 7}))
    qty_7_days = response.json()['qty']

    # Шаг 7: Проверяем количество за 30 дней (должно быть >= qty_7_days)
    response = client.get(reverse('api__get_qty_of_added_visited_countries', kwargs={'days': 30}))
    qty_30_days = response.json()['qty']

    # Шаг 8: Проверяем что количество увеличивается с увеличением дней
    assert qty_1_day >= 0
    assert qty_7_days >= qty_1_day
    assert qty_30_days >= qty_7_days


@pytest.mark.e2e
@pytest.mark.django_db
def test_dashboard_complete_user_journey(client: Client, django_user_model: Any) -> None:
    """Полный сценарий работы пользователя с dashboard"""
    # Шаг 1: Создаем обычного пользователя
    regular_user = django_user_model.objects.create_user(username='regular', password='pass')

    # Шаг 2: Пытаемся получить доступ к dashboard - неудача
    client.force_login(regular_user)
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302

    # Шаг 3: Выходим и создаем суперюзера
    client.logout()
    superuser = django_user_model.objects.create_superuser(username='admin', password='adminpass')

    # Шаг 4: Авторизуемся как суперюзер
    client.force_login(superuser)

    # Шаг 5: Открываем dashboard
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert 'Dashboard' in str(response.content)

    # Шаг 6: Проверяем базовую статистику
    assert response.context['qty_users'] == 2  # regular + superuser

    # Шаг 7: Проверяем все API endpoints
    api_endpoints = [
        ('api__get_total_visited_countries', {}),
        ('api__get_qty_users_with_visited_countries', {}),
        ('api__get_average_qty_visited_countries', {}),
        ('api__max_qty_visited_countries', {}),
        ('api__get_qty_of_added_visited_countries', {'days': 1}),
        ('api__get_added_visited_countries_by_day', {}),
    ]

    for endpoint_name, kwargs in api_endpoints:
        url = reverse(endpoint_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    # Шаг 8: Добавляем данные и проверяем обновление
    country = Country.objects.create(name='Тест', code='TS')
    region_type3 = RegionType.objects.create(title='Регион')
    region = Region.objects.create(
        title='Тестовый', country=country, type=region_type3, iso3166='TS-TST-E2E'
    )
    city = City.objects.create(
        title='Тестовый',
        region=region,
        country=country,
        coordinate_width=0.0,
        coordinate_longitude=0.0,
    )
    VisitedCity.objects.create(
        user=regular_user,
        city=city,
        date_of_visit=date.today(),
        rating=5,
        has_magnet=True,
    )

    # Шаг 9: Обновляем dashboard
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert response.context['qty_visited_cities'] == 1

    # Шаг 10: Выходим
    client.logout()

    # Шаг 11: Проверяем что dashboard недоступен
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    # LoginRequiredMixin редиректит на LOGIN_URL
    assert str(response.url) == '/'  # type: ignore[attr-defined]
