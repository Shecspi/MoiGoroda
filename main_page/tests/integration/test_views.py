"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any

from django.test import Client
from django.urls import reverse


# ===== Integration тесты для главной страницы =====


@pytest.mark.integration
@pytest.mark.django_db
def test_main_page_shows_content_for_unauthenticated_user(client: Client) -> None:
    """Тест что главная страница отображается для неаутентифицированного пользователя."""
    response = client.get(reverse('main_page'))

    assert response.status_code == 200
    assert 'index.html' in [t.name for t in response.templates]


@pytest.mark.integration
@pytest.mark.django_db
def test_main_page_context_for_unauthenticated_user(client: Client) -> None:
    """Тест что контекст главной страницы содержит правильные данные."""
    response = client.get(reverse('main_page'))

    assert response.status_code == 200
    assert 'page_title' in response.context
    assert 'page_description' in response.context
    assert response.context['page_title'] == 'Сервис учёта посещённых городов «Мои города»'
    assert (
        response.context['page_description']
        == '«Мои города» — сервис учёта посещённых городов: отмечайте города и страны, смотрите их на карте, открывайте новые направления и следите за поездками друзей'
    )


@pytest.mark.integration
@pytest.mark.django_db
def test_main_page_redirects_authenticated_user(client: Client, django_user_model: Any) -> None:
    """Тест что главная страница перенаправляет аутентифицированного пользователя."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    client.force_login(user)

    response = client.get(reverse('main_page'))

    assert response.status_code == 302
    assert str(response.url) == reverse('city-all-list')  # type: ignore[attr-defined]


@pytest.mark.integration
@pytest.mark.django_db
def test_main_page_url_resolves_correctly(client: Client) -> None:
    """Тест что URL главной страницы правильно разрешается."""
    # Проверяем что URL '' (корень) соответствует view 'main_page'
    response = client.get('/')

    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
def test_main_page_uses_correct_template(client: Client) -> None:
    """Тест что главная страница использует правильный шаблон."""
    response = client.get(reverse('main_page'))

    assert response.status_code == 200
    # Проверяем что используется шаблон index.html
    template_names = [t.name for t in response.templates]
    assert 'index.html' in template_names


@pytest.mark.integration
@pytest.mark.django_db
def test_main_page_accessible_via_root_url(client: Client) -> None:
    """Тест что главная страница доступна по корневому URL."""
    response = client.get('/')

    assert response.status_code == 200
    assert 'index.html' in [t.name for t in response.templates]


@pytest.mark.integration
@pytest.mark.django_db
def test_main_page_does_not_redirect_anonymous(client: Client) -> None:
    """Тест что главная страница не перенаправляет анонимного пользователя."""
    response = client.get(reverse('main_page'))

    # Анонимный пользователь должен получить 200, а не редирект
    assert response.status_code == 200
    # Для обычного ответа (не редиректа) атрибут url не должен существовать
    assert not hasattr(response, 'url')


@pytest.mark.integration
@pytest.mark.django_db
def test_main_page_redirect_preserves_correct_destination(
    client: Client, django_user_model: Any
) -> None:
    """Тест что редирект аутентифицированного пользователя ведет на правильную страницу."""
    user = django_user_model.objects.create_user(username='user123', password='pass123')
    client.force_login(user)

    response = client.get(reverse('main_page'))

    assert response.status_code == 302
    # Проверяем что редирект именно на city-all-list
    assert response.url == reverse('city-all-list')  # type: ignore[attr-defined]


@pytest.mark.integration
@pytest.mark.django_db
def test_main_page_different_users_redirect_to_same_page(
    client: Client, django_user_model: Any
) -> None:
    """Тест что разные аутентифицированные пользователи редиректятся на одну страницу."""
    user1 = django_user_model.objects.create_user(username='user1', password='pass1')
    user2 = django_user_model.objects.create_user(username='user2', password='pass2')

    # Проверяем первого пользователя
    client.force_login(user1)
    response1 = client.get(reverse('main_page'))

    # Проверяем второго пользователя
    client.force_login(user2)
    response2 = client.get(reverse('main_page'))

    assert response1.status_code == 302
    assert response2.status_code == 302
    assert response1.url == response2.url  # type: ignore[attr-defined]
    assert response1.url == reverse('city-all-list')  # type: ignore[attr-defined]
