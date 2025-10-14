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
def test_place_view_authenticated(client: Any, django_user_model: Any) -> None:
    """Тест доступа к странице мест авторизованным пользователем"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    url = reverse('place_map')
    response = client.get(url)

    assert response.status_code == 200
    assert 'page_title' in response.context
    assert response.context['page_title'] == 'Мои места'
    assert response.context['page_description'] == 'Мои места, отмеченные на карте'
    assert response.context['active_page'] == 'places'


@pytest.mark.integration
@pytest.mark.django_db
def test_place_view_unauthenticated(client: Any) -> None:
    """Тест что неавторизованный пользователь перенаправляется на страницу входа"""
    url = reverse('place_map')
    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith('/account/signin')


@pytest.mark.integration
@pytest.mark.django_db
def test_place_view_template(client: Any, django_user_model: Any) -> None:
    """Тест что используется правильный шаблон"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    url = reverse('place_map')
    response = client.get(url)

    assert response.status_code == 200
    assert 'place/map.html' in (t.name for t in response.templates)


@pytest.mark.integration
@pytest.mark.django_db
def test_place_view_context(client: Any, django_user_model: Any) -> None:
    """Тест контекста страницы мест"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    url = reverse('place_map')
    response = client.get(url)

    assert response.status_code == 200
    context = response.context

    # Проверяем наличие всех необходимых ключей
    assert 'page_title' in context
    assert 'page_description' in context
    assert 'active_page' in context

    # Проверяем значения
    assert context['page_title'] == 'Мои места'
    assert context['page_description'] == 'Мои места, отмеченные на карте'
    assert context['active_page'] == 'places'


@pytest.mark.integration
@pytest.mark.django_db
def test_place_view_multiple_access(client: Any, django_user_model: Any) -> None:
    """Тест многократного доступа к странице мест"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    url = reverse('place_map')

    # Первый доступ
    response1 = client.get(url)
    assert response1.status_code == 200

    # Второй доступ
    response2 = client.get(url)
    assert response2.status_code == 200

    # Третий доступ
    response3 = client.get(url)
    assert response3.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
def test_place_view_after_logout(client: Any, django_user_model: Any) -> None:
    """Тест доступа к странице мест после выхода"""
    user = django_user_model.objects.create_user(username='testuser', password='password123')
    client.force_login(user)

    url = reverse('place_map')
    response = client.get(url)
    assert response.status_code == 200

    # Выход
    client.logout()

    # Попытка доступа после выхода
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith('/account/signin')
