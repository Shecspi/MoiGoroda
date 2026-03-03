"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

import os
from typing import Any

from django.db.models import Q
from django.http import HttpRequest
from dotenv import load_dotenv

from MoiGoroda import settings
from news.models import News
from premium.models import PremiumSubscription

load_dotenv()


def general_settings(request: HttpRequest) -> dict[str, Any]:
    """
    Контекстный процессор для общих настроек приложения.

    Добавляет в контекст шаблонов общие настройки из переменных окружения,
    информацию о непрочитанных новостях и об активной премиум-подписке пользователя.

    Args:
        request: HTTP-запрос от клиента.

    Returns:
        dict: Словарь с настройками приложения и данными для шаблонов.
    """
    has_unread_news = False
    active_subscription = None
    if request.user.is_authenticated:
        # Список ID новостей, которые пользователь уже прочитал
        users_read_news = News.users_read.through.objects.filter(
            user_id=request.user.id
        ).values_list('news_id', flat=True)
        # True, если есть хотя бы одна новость, ID которой нет в user_read_news
        has_unread_news = News.objects.filter(~Q(id__in=users_read_news)).exists()
        # Активная премиум-подписка (для проверки доступа к функциям)
        active_subscription = (
            PremiumSubscription.objects.filter(
                user=request.user,
                status=PremiumSubscription.Status.ACTIVE,
            )
            .select_related('plan')
            .prefetch_related('plan__features')
            .first()
        )

    context: dict[str, Any] = {
        'SITE_NAME': os.getenv('SITE_NAME'),
        'SITE_URL': os.getenv('SITE_URL'),
        'PROJECT_VERSION': os.getenv('PROJECT_VERSION'),
        'API_YANDEX_MAP': os.getenv('API_YANDEX_MAP'),
        'YANDEX_METRIKA': os.getenv('YANDEX_METRIKA'),
        'SUPPORT_EMAIL': os.getenv('DEFAULT_FROM_EMAIL'),
        'has_unread_news': has_unread_news,
        'active_subscription': active_subscription,
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
