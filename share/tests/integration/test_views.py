"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from django.urls import reverse


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_with_valid_user_dashboard(
    client: Any, test_user_with_share_settings: Any
) -> None:
    """Тест доступа к странице публикации dashboard авторизованным пользователем"""
    url = reverse(
        'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'dashboard'}
    )
    response = client.get(url)

    assert response.status_code == 200
    assert 'username' in response.context
    assert response.context['username'] == 'testuser'


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_with_invalid_user(client: Any) -> None:
    """Тест доступа к странице публикации с невалидным пользователем"""
    url = reverse('share', kwargs={'pk': 99999, 'requested_page': 'dashboard'})
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_user_without_settings(
    client: Any, test_user_without_share_settings: Any
) -> None:
    """Тест доступа к странице публикации пользователя без настроек"""
    url = reverse(
        'share', kwargs={'pk': test_user_without_share_settings.id, 'requested_page': 'dashboard'}
    )
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_user_with_all_disabled(client: Any, django_user_model: Any) -> None:
    """Тест доступа к странице публикации когда все опции отключены"""
    from account.models import ShareSettings

    user = django_user_model.objects.create_user(username='testuser3', password='password123')
    ShareSettings.objects.create(
        user=user,
        can_share_dashboard=False,
        can_share_city_map=False,
        can_share_region_map=False,
    )

    url = reverse('share', kwargs={'pk': user.id, 'requested_page': 'dashboard'})
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_city_map(client: Any, test_user_with_share_settings: Any) -> None:
    """Тест доступа к странице карты городов"""
    url = reverse(
        'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'city_map'}
    )
    response = client.get(url)

    assert response.status_code == 200
    assert 'username' in response.context
    assert response.context['displayed_page'] == 'city_map'


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_region_map_without_country(
    client: Any, test_user_with_share_settings: Any
) -> None:
    """Тест доступа к странице карты регионов без кода страны"""
    url = reverse(
        'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'region_map'}
    )
    response = client.get(url)

    # Должен быть редирект на страницу с кодом страны
    assert response.status_code == 302


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_region_map_with_country(
    client: Any, test_user_with_share_settings: Any
) -> None:
    """Тест доступа к странице карты регионов с кодом страны"""
    from country.models import Country

    Country.objects.create(name='Россия', code='RU')

    url = (
        reverse(
            'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'region_map'}
        )
        + '?country=RU'
    )
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['country_code'] == 'RU'


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_without_requested_page(client: Any, test_user_with_share_settings: Any) -> None:
    """Тест доступа к странице публикации без указания страницы"""
    url = reverse('share', kwargs={'pk': test_user_with_share_settings.id})
    response = client.get(url)

    # Должна отобразиться первая доступная страница
    assert response.status_code in [200, 302]


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_fallback_to_alternative_page(client: Any, django_user_model: Any) -> None:
    """Тест переключения на альтернативную страницу"""
    from account.models import ShareSettings

    user = django_user_model.objects.create_user(username='testuser4', password='password123')
    ShareSettings.objects.create(
        user=user,
        can_share_dashboard=False,
        can_share_city_map=True,
        can_share_region_map=False,
    )

    url = reverse('share', kwargs={'pk': user.id, 'requested_page': 'dashboard'})
    response = client.get(url)

    # Должен быть редирект на city_map
    assert response.status_code == 302


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_context_contains_permissions(
    client: Any, test_user_with_share_settings: Any
) -> None:
    """Тест что контекст содержит информацию о правах доступа"""
    url = reverse(
        'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'dashboard'}
    )
    response = client.get(url)

    assert response.status_code == 200
    assert 'can_share_dashboard' in response.context
    assert 'can_share_city_map' in response.context
    assert 'can_share_region_map' in response.context
    assert 'can_subscribe' in response.context


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_template_name_dashboard(
    client: Any, test_user_with_share_settings: Any
) -> None:
    """Тест что используется правильный шаблон для dashboard"""
    url = reverse(
        'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'dashboard'}
    )
    response = client.get(url)

    assert response.status_code == 200
    assert 'share/dashboard.html' in (t.name for t in response.templates)


@pytest.mark.integration
@pytest.mark.django_db
def test_share_view_template_name_city_map(client: Any, test_user_with_share_settings: Any) -> None:
    """Тест что используется правильный шаблон для city_map"""
    url = reverse(
        'share', kwargs={'pk': test_user_with_share_settings.id, 'requested_page': 'city_map'}
    )
    response = client.get(url)

    assert response.status_code == 200
    assert 'share/city_map.html' in (t.name for t in response.templates)
