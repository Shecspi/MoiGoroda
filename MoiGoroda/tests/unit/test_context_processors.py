"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from MoiGoroda.context_processors import general_settings


# ===== Unit тесты для context_processors =====


@pytest.fixture
def request_factory() -> RequestFactory:
    """Фикстура для создания HTTP-запросов."""
    return RequestFactory()


@pytest.fixture
def mock_env_vars() -> dict[str, str]:
    """Фикстура с мок-данными переменных окружения."""
    return {
        'SITE_NAME': 'Test Site',
        'SITE_URL': 'https://test.com',
        'PROJECT_VERSION': '1.0.0',
        'API_YANDEX_MAP': 'test-api-key',
        'YANDEX_METRIKA': 'test-metrika',
        'DEFAULT_FROM_EMAIL': 'test@test.com',
        'DONATE_LINK': 'https://donate.test.com',
        'URL_GEO_POLYGONS': 'https://geo.test.com',
        'TILE_LAYER': 'test-layer',
        'SIDEBAR_LINK_URL': 'https://sidebar.test.com',
        'SIDEBAR_LINK_TEXT': 'Test Link',
        'SIDEBAR_LINK_ADV_INFO': 'Test Info',
    }


@pytest.mark.unit
def test_general_settings_returns_dict(request_factory: RequestFactory) -> None:
    """Тест что general_settings возвращает словарь."""
    request = request_factory.get('/')
    request.user = AnonymousUser()

    context = general_settings(request)

    assert isinstance(context, dict)


@pytest.mark.unit
def test_general_settings_contains_all_required_keys(request_factory: RequestFactory) -> None:
    """Тест что контекст содержит все необходимые ключи."""
    request = request_factory.get('/')
    request.user = AnonymousUser()

    context = general_settings(request)

    required_keys = [
        'SITE_NAME',
        'SITE_URL',
        'PROJECT_VERSION',
        'API_YANDEX_MAP',
        'YANDEX_METRIKA',
        'SUPPORT_EMAIL',
        'has_unread_news',
        'DONATE_LINK',
        'URL_GEO_POLYGONS',
        'TILE_LAYER',
        'SIDEBAR_LINK_URL',
        'SIDEBAR_LINK_TEXT',
        'SIDEBAR_LINK_ADV_INFO',
        'DEBUG',
        'PRIVACY_POLICY_VERSION',
    ]

    for key in required_keys:
        assert key in context


@pytest.mark.unit
def test_general_settings_has_unread_news_false_for_anonymous(
    request_factory: RequestFactory,
) -> None:
    """Тест что has_unread_news=False для анонимного пользователя."""
    request = request_factory.get('/')
    request.user = AnonymousUser()

    context = general_settings(request)

    assert context['has_unread_news'] is False


@pytest.mark.unit
@pytest.mark.django_db
def test_general_settings_has_unread_news_false_for_authenticated_no_news(
    request_factory: RequestFactory, django_user_model: Any
) -> None:
    """Тест что has_unread_news=False когда нет новостей."""
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    request = request_factory.get('/')
    request.user = user

    context = general_settings(request)

    assert context['has_unread_news'] is False


@pytest.mark.unit
@pytest.mark.django_db
def test_general_settings_has_unread_news_true_when_unread_exists(
    request_factory: RequestFactory, django_user_model: Any
) -> None:
    """Тест что has_unread_news=True когда есть непрочитанные новости."""
    from news.models import News

    user = django_user_model.objects.create_user(username='testuser', password='testpass')

    # Создаем новость
    News.objects.create(title='Test News', content='Test content')

    request = request_factory.get('/')
    request.user = user

    context = general_settings(request)

    # Должно быть True, так как есть новость, которую пользователь не читал
    assert context['has_unread_news'] is True


@pytest.mark.unit
@pytest.mark.django_db
def test_general_settings_has_unread_news_false_when_all_read(
    request_factory: RequestFactory, django_user_model: Any
) -> None:
    """Тест что has_unread_news=False когда все новости прочитаны."""
    from news.models import News

    user = django_user_model.objects.create_user(username='testuser', password='testpass')

    # Создаем новость
    news = News.objects.create(title='Test News', content='Test content')

    # Отмечаем новость как прочитанную
    news.users_read.add(user)

    request = request_factory.get('/')
    request.user = user

    context = general_settings(request)

    # Должно быть False, так как все новости прочитаны
    assert context['has_unread_news'] is False


@pytest.mark.unit
@pytest.mark.django_db
def test_general_settings_has_unread_news_true_with_multiple_news(
    request_factory: RequestFactory, django_user_model: Any
) -> None:
    """Тест что has_unread_news=True когда есть хотя бы одна непрочитанная новость."""
    from news.models import News

    user = django_user_model.objects.create_user(username='testuser', password='testpass')

    # Создаем несколько новостей
    news1 = News.objects.create(title='News 1', content='Content 1')
    news2 = News.objects.create(title='News 2', content='Content 2')
    News.objects.create(title='News 3', content='Content 3')  # Непрочитанная новость

    # Отмечаем первые две как прочитанные
    news1.users_read.add(user)
    news2.users_read.add(user)

    request = request_factory.get('/')
    request.user = user

    context = general_settings(request)

    # Должно быть True, так как news3 не прочитана
    assert context['has_unread_news'] is True


@pytest.mark.unit
def test_general_settings_env_vars_integration(
    request_factory: RequestFactory, mock_env_vars: dict[str, str]
) -> None:
    """Тест интеграции с переменными окружения."""
    request = request_factory.get('/')
    request.user = AnonymousUser()

    with patch.dict('os.environ', mock_env_vars):
        with patch('MoiGoroda.context_processors.os.getenv', side_effect=mock_env_vars.get):
            context = general_settings(request)

            assert context['SITE_NAME'] == 'Test Site'
            assert context['SITE_URL'] == 'https://test.com'
            assert context['PROJECT_VERSION'] == '1.0.0'
            assert context['SUPPORT_EMAIL'] == 'test@test.com'


@pytest.mark.unit
def test_general_settings_debug_flag(request_factory: RequestFactory) -> None:
    """Тест что DEBUG флаг передается в контекст."""
    request = request_factory.get('/')
    request.user = AnonymousUser()

    context = general_settings(request)

    assert 'DEBUG' in context
    assert isinstance(context['DEBUG'], bool)


@pytest.mark.unit
def test_general_settings_privacy_policy_version(request_factory: RequestFactory) -> None:
    """Тест что PRIVACY_POLICY_VERSION передается в контекст."""
    request = request_factory.get('/')
    request.user = AnonymousUser()

    context = general_settings(request)

    assert 'PRIVACY_POLICY_VERSION' in context


@pytest.mark.unit
def test_general_settings_handles_none_env_vars(request_factory: RequestFactory) -> None:
    """Тест что функция корректно обрабатывает None значения из os.getenv."""
    request = request_factory.get('/')
    request.user = AnonymousUser()

    with patch('MoiGoroda.context_processors.os.getenv', return_value=None):
        context = general_settings(request)

        # Все переменные окружения должны быть None
        assert context['SITE_NAME'] is None
        assert context['SITE_URL'] is None
        assert context['API_YANDEX_MAP'] is None


@pytest.mark.unit
def test_general_settings_different_request_methods(request_factory: RequestFactory) -> None:
    """Тест что функция работает с разными HTTP методами."""
    request_get = request_factory.get('/')
    request_get.user = AnonymousUser()

    request_post = request_factory.post('/')
    request_post.user = AnonymousUser()

    context_get = general_settings(request_get)
    context_post = general_settings(request_post)

    # Контекст должен быть одинаковым независимо от метода
    assert 'has_unread_news' in context_get
    assert 'has_unread_news' in context_post
    assert context_get['has_unread_news'] == context_post['has_unread_news']
