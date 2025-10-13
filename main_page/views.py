"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def index(request: HttpRequest) -> HttpResponse:
    """
    Отображает главную страницу сервиса.

    Если пользователь аутентифицирован, перенаправляет на страницу списка всех городов.
    Если пользователь не аутентифицирован, отображает главную страницу с описанием сервиса.

    Args:
        request: HTTP-запрос от клиента.

    Returns:
        HttpResponse: Редирект на 'city-all-list' для аутентифицированных пользователей
                     или отрендеренный шаблон 'index.html' для неаутентифицированных.
    """
    if request.user.is_authenticated:
        return redirect('city-all-list')
    else:
        return render(
            request,
            'index.html',
            context={
                'page_title': 'Сервис учёта посещённых городов «Мои города»',
                'page_description': '«Мои города» — сервис учёта посещённых городов: отмечайте города и страны, смотрите их на карте, открывайте новые направления и следите за поездками друзей',
            },
        )
