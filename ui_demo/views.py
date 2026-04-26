"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render


def _guard(request: HttpRequest) -> None:
    if not settings.DEBUG:
        raise Http404()
    if not request.user.is_superuser:
        raise PermissionDenied()


def _render(
    request: HttpRequest,
    template: str,
    page_title: str,
    page_description: str = '',
    extra_context: dict[str, Any] | None = None,
) -> HttpResponse:
    _guard(request)
    context = {
        'page_title': page_title,
        'page_description': page_description,
        'active_page': 'ui_demo',
    }
    if extra_context:
        context.update(extra_context)

    return render(
        request,
        template,
        context,
    )


@login_required
def index(request: HttpRequest) -> HttpResponse:
    return _render(request, 'ui_demo/index.html', 'UI kit (демо)')


@login_required
def buttons(request: HttpRequest) -> HttpResponse:
    return _render(request, 'ui_demo/buttons.html', 'Кнопки')


@login_required
def badges(request: HttpRequest) -> HttpResponse:
    return _render(request, 'ui_demo/badges.html', 'Бейджи')


@login_required
def forms(request: HttpRequest) -> HttpResponse:
    demo_combobox_options = [
        {'value': 'moscow', 'label': 'Москва'},
        {'value': 'saint-petersburg', 'label': 'Санкт-Петербург'},
        {'value': 'kazan', 'label': 'Казань'},
        {'value': 'novosibirsk', 'label': 'Новосибирск'},
        {'value': 'yekaterinburg', 'label': 'Екатеринбург'},
        {'value': 'nizhny-novgorod', 'label': 'Нижний Новгород'},
    ]
    demo_select_search_options = [
        {'value': '', 'label': 'Выберите значение', 'selected': True},
        {'value': '1', 'label': 'Первый'},
        {'value': '2', 'label': 'Второй'},
        {'value': '3', 'label': 'Третий'},
    ]

    return _render(
        request,
        'ui_demo/forms.html',
        'Поля форм',
        extra_context={
            'demo_combobox_options': demo_combobox_options,
            'demo_select_search_options': demo_select_search_options,
        },
    )


@login_required
def misc(request: HttpRequest) -> HttpResponse:
    return _render(request, 'ui_demo/misc.html', 'Прочее')
