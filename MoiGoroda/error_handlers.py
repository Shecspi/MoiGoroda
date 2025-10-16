"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django.http import HttpRequest
from django.template.response import TemplateResponse


def page403(request: HttpRequest, exception: Any) -> TemplateResponse:
    """
    Обработчик ошибки 403 (Доступ запрещен).

    Args:
        request: HTTP-запрос от клиента.
        exception: Исключение, вызвавшее ошибку 403.

    Returns:
        TemplateResponse: Ответ с шаблоном error/403.html и статусом 403.
    """
    return TemplateResponse(
        request, 'error/403.html', status=403, context={'page_title': 'Отказано в доступе'}
    )


def page404(request: HttpRequest, exception: Any) -> TemplateResponse:
    """
    Обработчик ошибки 404 (Страница не найдена).

    Args:
        request: HTTP-запрос от клиента.
        exception: Исключение, вызвавшее ошибку 404.

    Returns:
        TemplateResponse: Ответ с шаблоном error/404.html и статусом 404.
    """
    return TemplateResponse(
        request, 'error/404.html', status=404, context={'page_title': 'Страница не найдена'}
    )


def page500(request: HttpRequest) -> TemplateResponse:
    """
    Обработчик ошибки 500 (Внутренняя ошибка сервера).

    Args:
        request: HTTP-запрос от клиента.

    Returns:
        TemplateResponse: Ответ с шаблоном error/500.html и статусом 500.
    """
    return TemplateResponse(
        request, 'error/500.html', status=500, context={'page_title': 'Внутренняя ошибка'}
    )
