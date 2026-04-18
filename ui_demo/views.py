"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

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
) -> HttpResponse:
    _guard(request)
    return render(
        request,
        template,
        {
            'page_title': page_title,
            'page_description': page_description,
            'active_page': 'ui_demo',
        },
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
    return _render(request, 'ui_demo/forms.html', 'Поля форм')


@login_required
def stat_badges(request: HttpRequest) -> HttpResponse:
    return _render(request, 'ui_demo/stat_badges.html', 'Статистические бейджи')


@login_required
def misc(request: HttpRequest) -> HttpResponse:
    return _render(request, 'ui_demo/misc.html', 'Прочее')

