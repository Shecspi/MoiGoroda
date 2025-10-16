"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from django.urls import reverse


# ===== E2E тесты для полного цикла работы с публикацией =====


@pytest.mark.e2e
@pytest.mark.django_db
def test_complete_share_workflow(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Полный цикл публикации статистики
    Создание пользователя -> Настройка прав -> Просмотр публикации -> Переключение страниц
    """
    from account.models import ShareSettings

    # Шаг 1: Создаём пользователя
    user = django_user_model.objects.create_user(username='shareuser', password='password123')

    # Шаг 2: Создаём настройки публикации
    ShareSettings.objects.create(
        user=user,
        can_share_dashboard=True,
        can_share_city_map=True,
        can_share_region_map=True,
        can_subscribe=True,
    )

    # Шаг 3: Открываем страницу публикации без указания типа
    url = reverse('share', kwargs={'pk': user.id})
    response = client.get(url, follow=True)
    assert response.status_code == 200

    # Шаг 4: Открываем dashboard
    url = reverse('share', kwargs={'pk': user.id, 'requested_page': 'dashboard'})
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['displayed_page'] == 'dashboard'

    # Шаг 5: Открываем city_map
    url = reverse('share', kwargs={'pk': user.id, 'requested_page': 'city_map'})
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['displayed_page'] == 'city_map'

    # Шаг 6: Открываем region_map
    url = reverse('share', kwargs={'pk': user.id, 'requested_page': 'region_map'}) + '?country=RU'
    response = client.get(url, follow=True)
    # Может быть 200 или 404 если страна не существует
    assert response.status_code in [200, 404]


@pytest.mark.e2e
@pytest.mark.django_db
def test_share_permissions_workflow(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Работа с правами доступа
    Пользователь отключает разные опции -> Проверяем редиректы и доступ
    """
    from account.models import ShareSettings

    # Шаг 1: Создаём пользователя с частичными правами
    user = django_user_model.objects.create_user(username='partialuser', password='password123')

    ShareSettings.objects.create(
        user=user,
        can_share_dashboard=False,
        can_share_city_map=True,
        can_share_region_map=False,
    )

    # Шаг 2: Пытаемся открыть dashboard (недоступен)
    url = reverse('share', kwargs={'pk': user.id, 'requested_page': 'dashboard'})
    response = client.get(url)
    # Должен быть редирект на city_map
    assert response.status_code == 302

    # Шаг 3: Переходим по редиректу
    response = client.get(url, follow=True)
    assert response.status_code == 200
    assert response.context['displayed_page'] == 'city_map'

    # Шаг 4: Пытаемся открыть region_map (недоступен)
    url = reverse('share', kwargs={'pk': user.id, 'requested_page': 'region_map'})
    response = client.get(url)
    # Должен быть редирект
    assert response.status_code == 302


@pytest.mark.e2e
@pytest.mark.django_db
def test_share_multiple_users_isolation(client: Any, django_user_model: Any) -> None:
    """
    E2E тест: Изоляция публикаций между пользователями
    Два пользователя с разными настройками
    """
    from account.models import ShareSettings

    # Шаг 1: Создаём двух пользователей
    user1 = django_user_model.objects.create_user(username='user1', password='password123')
    user2 = django_user_model.objects.create_user(username='user2', password='password123')

    # Шаг 2: Настраиваем права для user1 (только dashboard)
    ShareSettings.objects.create(
        user=user1,
        can_share_dashboard=True,
        can_share_city_map=False,
        can_share_region_map=False,
    )

    # Шаг 3: Настраиваем права для user2 (только city_map)
    ShareSettings.objects.create(
        user=user2,
        can_share_dashboard=False,
        can_share_city_map=True,
        can_share_region_map=False,
    )

    # Шаг 4: Проверяем user1 - dashboard доступен
    url = reverse('share', kwargs={'pk': user1.id, 'requested_page': 'dashboard'})
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['displayed_page'] == 'dashboard'

    # Шаг 5: Проверяем user1 - city_map недоступен, редирект на dashboard
    url = reverse('share', kwargs={'pk': user1.id, 'requested_page': 'city_map'})
    response = client.get(url)
    assert response.status_code == 302

    # Шаг 6: Проверяем user2 - city_map доступен
    url = reverse('share', kwargs={'pk': user2.id, 'requested_page': 'city_map'})
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['displayed_page'] == 'city_map'

    # Шаг 7: Проверяем user2 - dashboard недоступен, редирект на city_map
    url = reverse('share', kwargs={'pk': user2.id, 'requested_page': 'dashboard'})
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.e2e
@pytest.mark.django_db
def test_share_with_country_selection(client: Any, test_user_with_share_settings: Any) -> None:
    """
    E2E тест: Работа с выбором страны для карты регионов
    """
    from country.models import Country

    # Шаг 1: Создаём страны
    Country.objects.create(name='Россия', code='RU')
    Country.objects.create(name='США', code='US')

    # Шаг 2: Открываем region_map без страны - должен быть редирект
    url = reverse(
        'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'region_map'}
    )
    response = client.get(url)
    assert response.status_code == 302

    # Шаг 3: Открываем region_map с Россией
    url = (
        reverse(
            'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'region_map'}
        )
        + '?country=RU'
    )
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['country_code'] == 'RU'

    # Шаг 4: Открываем region_map с США
    url = (
        reverse(
            'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'region_map'}
        )
        + '?country=US'
    )
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['country_code'] == 'US'

    # Шаг 5: Открываем region_map с невалидной страной
    url = (
        reverse(
            'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'region_map'}
        )
        + '?country=INVALID'
    )
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.e2e
@pytest.mark.django_db
def test_share_context_data(client: Any, test_user_with_share_settings: Any) -> None:
    """
    E2E тест: Проверка всех данных контекста
    """
    # Шаг 1: Открываем dashboard
    url = reverse(
        'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'dashboard'}
    )
    response = client.get(url)

    assert response.status_code == 200

    # Шаг 2: Проверяем наличие всех обязательных ключей
    context = response.context
    assert 'username' in context
    assert 'user_id' in context
    assert 'displayed_page' in context
    assert 'can_share_dashboard' in context
    assert 'can_share_city_map' in context
    assert 'can_share_region_map' in context
    assert 'can_subscribe' in context
    assert 'page_title' in context
    assert 'page_description' in context

    # Шаг 3: Проверяем значения
    assert context['username'] == 'testuser'
    assert context['user_id'] == test_user_with_share_settings.id
    assert context['displayed_page'] == 'dashboard'
    assert context['can_share_dashboard'] is True
    assert context['can_share_city_map'] is True
    assert context['can_share_region_map'] is True
