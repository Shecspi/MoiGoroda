"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import os

from django.db.models import Q
from django.http import HttpRequest
from dotenv import load_dotenv

from MoiGoroda import settings
from news.models import News

load_dotenv()


def general_settings(request: HttpRequest) -> dict[str, str | bool | None]:
    """
    Контекстный процессор для общих настроек приложения.

    Добавляет в контекст шаблонов общие настройки из переменных окружения,
    а также информацию о наличии непрочитанных новостей для аутентифицированного пользователя.

    Args:
        request: HTTP-запрос от клиента.

    Returns:
        dict: Словарь с настройками приложения и данными о непрочитанных новостях.
    """
    has_unread_news = False
    if request.user.is_authenticated:
        # Список ID новостей, которые пользователь уже прочитал
        users_read_news = News.users_read.through.objects.filter(
            user_id=request.user.id
        ).values_list('news_id', flat=True)
        # True, если есть хотя бы одна новость, ID которой нет в user_read_news
        has_unread_news = News.objects.filter(~Q(id__in=users_read_news)).exists()

    context: dict[str, str | bool | None] = {
        'SITE_NAME': os.getenv('SITE_NAME'),
        'SITE_URL': os.getenv('SITE_URL'),
        'PROJECT_VERSION': os.getenv('PROJECT_VERSION'),
        'API_YANDEX_MAP': os.getenv('API_YANDEX_MAP'),
        'YANDEX_METRIKA': os.getenv('YANDEX_METRIKA'),
        'SUPPORT_EMAIL': os.getenv('DEFAULT_FROM_EMAIL'),
        'has_unread_news': has_unread_news,
        'DONATE_LINK': os.getenv('DONATE_LINK'),
        'URL_GEO_POLYGONS': os.getenv('URL_GEO_POLYGONS'),
        'TILE_LAYER': os.getenv('TILE_LAYER'),
        'SIDEBAR_LINK_URL': os.getenv('SIDEBAR_LINK_URL'),
        'SIDEBAR_LINK_TEXT': os.getenv('SIDEBAR_LINK_TEXT'),
        'SIDEBAR_LINK_ADV_INFO': os.getenv('SIDEBAR_LINK_ADV_INFO'),
        'DEBUG': settings.DEBUG,
        'PRIVACY_POLICY_VERSION': settings.PRIVACY_POLICY_VERSION,
    }

    return context
