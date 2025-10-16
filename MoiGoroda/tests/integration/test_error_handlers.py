"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from django.test import Client


# ===== Integration тесты для обработчиков ошибок =====


@pytest.mark.integration
@pytest.mark.django_db
def test_404_error_handler(client: Client) -> None:
    """Тест обработчика ошибки 404."""
    # Пытаемся получить несуществующую страницу
    response = client.get('/nonexistent-page/')

    assert response.status_code == 404
    assert 'error/404.html' in [t.name for t in response.templates]


@pytest.mark.integration
@pytest.mark.django_db
def test_404_error_handler_context(client: Client) -> None:
    """Тест контекста обработчика ошибки 404."""
    response = client.get('/nonexistent-url-12345/')

    assert response.status_code == 404
    assert 'page_title' in response.context
    assert response.context['page_title'] == 'Страница не найдена'


@pytest.mark.integration
@pytest.mark.django_db
def test_404_error_handler_with_different_urls(client: Client) -> None:
    """Тест обработчика 404 с различными несуществующими URL."""
    urls = [
        '/does-not-exist/',
        '/random/path/',
        '/city/999999/',
    ]

    for url in urls:
        response = client.get(url)
        assert response.status_code == 404
        assert 'error/404.html' in [t.name for t in response.templates]


@pytest.mark.integration
@pytest.mark.django_db
def test_404_error_renders_template(client: Client) -> None:
    """Тест что обработчик 404 корректно рендерит шаблон."""
    response = client.get('/fake-page/')

    assert response.status_code == 404
    # Проверяем что шаблон был отрендерен
    assert response['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.integration
@pytest.mark.django_db
def test_403_error_handler_template_exists(client: Client) -> None:
    """Тест что шаблон для 403 ошибки существует."""
    # Мы не можем просто вызвать 403 ошибку через обычный запрос,
    # но можем проверить, что обработчик настроен правильно
    from MoiGoroda import urls

    assert hasattr(urls, 'handler403')
    assert urls.handler403 == 'MoiGoroda.error_handlers.page403'


@pytest.mark.integration
@pytest.mark.django_db
def test_404_error_handler_is_configured(client: Client) -> None:
    """Тест что обработчик 404 настроен в urls.py."""
    from MoiGoroda import urls

    assert hasattr(urls, 'handler404')
    assert urls.handler404 == 'MoiGoroda.error_handlers.page404'


@pytest.mark.integration
@pytest.mark.django_db
def test_500_error_handler_is_configured(client: Client) -> None:
    """Тест что обработчик 500 настроен в urls.py."""
    from MoiGoroda import urls

    assert hasattr(urls, 'handler500')
    assert urls.handler500 == 'MoiGoroda.error_handlers.page500'


@pytest.mark.integration
@pytest.mark.django_db
def test_404_error_with_query_params(client: Client) -> None:
    """Тест обработчика 404 с параметрами запроса."""
    response = client.get('/nonexistent/?param1=value1&param2=value2')

    assert response.status_code == 404
    assert 'error/404.html' in [t.name for t in response.templates]


@pytest.mark.integration
@pytest.mark.django_db
def test_404_error_with_post_request(client: Client) -> None:
    """Тест обработчика 404 с POST запросом."""
    response = client.post('/nonexistent/', data={'test': 'data'})

    assert response.status_code == 404
    assert 'error/404.html' in [t.name for t in response.templates]


@pytest.mark.integration
def test_error_handlers_functions_exist() -> None:
    """Тест что все функции обработчиков ошибок существуют."""
    from MoiGoroda.error_handlers import page403, page404, page500

    assert callable(page403)
    assert callable(page404)
    assert callable(page500)


@pytest.mark.integration
def test_error_handlers_return_template_response() -> None:
    """Тест что обработчики ошибок возвращают TemplateResponse."""
    from django.template.response import TemplateResponse
    from django.test import RequestFactory
    from MoiGoroda.error_handlers import page403, page404, page500

    factory = RequestFactory()
    request = factory.get('/')

    # Создаем фейковое исключение
    exception = Exception('Test exception')

    response_403 = page403(request, exception)
    response_404 = page404(request, exception)
    response_500 = page500(request)

    assert isinstance(response_403, TemplateResponse)
    assert isinstance(response_404, TemplateResponse)
    assert isinstance(response_500, TemplateResponse)


@pytest.mark.integration
def test_error_handlers_return_correct_status_codes() -> None:
    """Тест что обработчики ошибок возвращают корректные статус-коды."""
    from django.test import RequestFactory
    from MoiGoroda.error_handlers import page403, page404, page500

    factory = RequestFactory()
    request = factory.get('/')
    exception = Exception('Test exception')

    response_403 = page403(request, exception)
    response_404 = page404(request, exception)
    response_500 = page500(request)

    assert response_403.status_code == 403
    assert response_404.status_code == 404
    assert response_500.status_code == 500


@pytest.mark.integration
def test_error_handlers_use_correct_templates() -> None:
    """Тест что обработчики ошибок используют корректные шаблоны."""
    from django.test import RequestFactory
    from MoiGoroda.error_handlers import page403, page404, page500

    factory = RequestFactory()
    request = factory.get('/')
    exception = Exception('Test exception')

    response_403 = page403(request, exception)
    response_404 = page404(request, exception)
    response_500 = page500(request)

    assert response_403.template_name == 'error/403.html'
    assert response_404.template_name == 'error/404.html'
    assert response_500.template_name == 'error/500.html'


@pytest.mark.integration
def test_error_handlers_context_has_page_title() -> None:
    """Тест что обработчики ошибок добавляют page_title в контекст."""
    from MoiGoroda.error_handlers import page403, page404, page500

    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser

    factory = RequestFactory()
    request = factory.get('/')
    request.user = AnonymousUser()  # Добавляем пользователя для context processor
    exception = Exception('Test exception')

    response_403 = page403(request, exception)
    response_404 = page404(request, exception)
    response_500 = page500(request)

    # Проверяем что context содержит page_title без рендеринга
    # (рендеринг требует полной настройки шаблонов и middleware)
    assert 'page_title' in response_403.context_data  # type: ignore[operator]
    assert 'page_title' in response_404.context_data  # type: ignore[operator]
    assert 'page_title' in response_500.context_data  # type: ignore[operator]

    assert response_403.context_data['page_title'] == 'Отказано в доступе'  # type: ignore[index]
    assert response_404.context_data['page_title'] == 'Страница не найдена'  # type: ignore[index]
    assert response_500.context_data['page_title'] == 'Внутренняя ошибка'  # type: ignore[index]
