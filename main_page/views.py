"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.conf import settings


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


def help_premium_photos(request: HttpRequest) -> HttpResponse:
    """Отображает справку по загрузке фото в расширенной подписке."""
    return render(
        request,
        'help/premium_photos.html',
        context={
            'page_title': 'Справка: фотографии в расширенной подписке',
            'page_description': 'Как работает загрузка фотографий в расширенной подписке и что происходит с фото после её окончания',
            'city_user_photos_limit': settings.CITY_USER_PHOTOS_LIMIT,
            'city_user_photo_max_upload_mb': settings.CITY_USER_PHOTO_MAX_UPLOAD_MB,
        },
    )


def help_index(request: HttpRequest) -> HttpResponse:
    """Отображает главную страницу раздела справки."""
    help_articles = [
        {
            'title': 'Фотографии в премиум-доступе',
            'description': 'Как загружать фотографии, выбирать основное изображение и как работает хранение после окончания периода доступа.',
            'url': '/help/users-city-photos/',
        },
    ]
    return render(
        request,
        'help/index.html',
        context={
            'page_title': 'Справка',
            'page_description': 'Справочные материалы по возможностям сервиса',
            'help_articles': help_articles,
        },
    )
