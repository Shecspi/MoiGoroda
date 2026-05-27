"""
События продуктовой аналитики (источник UI при добавлении посещения города).
"""

from __future__ import annotations

from django.db import models
from django.db.models import CASCADE

from city.models import VisitedCity


class VisitedCityAddSource(models.Model):
    """
    Одна запись на успешно созданный VisitedCity: откуда пользователь пришёл к сохранению.
    """

    class Surface(models.TextChoices):
        SIDEBAR = 'sidebar', 'Сайдбар'
        CITY_LIST = 'city_list', 'Список городов'
        CITY_PAGE = 'city_page', 'Страница города'
        VISITED_CITIES_MAP = 'visited_cities_map', 'Карта посещённых городов'
        REGION_MAP = 'region_map', 'Карта городов региона'
        COLLECTION_PERSONAL_MAP = 'collection_personal_map', 'Карта персональной коллекции'
        COLLECTION_SELECTED_MAP = 'collection_selected_map', 'Карта коллекции сервиса'
        API_UNKNOWN = 'api_unknown', 'API без подсказки'
        UNKNOWN = 'unknown', 'Неизвестно'

    visited_city = models.OneToOneField(
        VisitedCity,
        on_delete=CASCADE,
        related_name='add_source_event',
        verbose_name='Посещение',
    )
    surface = models.CharField(
        max_length=64,
        choices=Surface.choices,
        db_index=True,
        verbose_name='Источник',
    )
    raw_hint = models.CharField(
        max_length=128,
        blank=True,
        default='',
        verbose_name='Сырой подсказка клиента',
        help_text='Например прежнее значение поля from в API',
    )
    recorded_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Записано',
    )

    class Meta:
        verbose_name = 'Источник добавления посещённого города'
        verbose_name_plural = 'Источники добавления посещённых городов'
        indexes = [
            models.Index(fields=['surface', 'recorded_at']),
        ]

    def __str__(self) -> str:
        return f'{self.surface} → {self.visited_city_id}'


class ModeSwitchLog(models.Model):
    """
    Лог переключения режима отображения городов: маркеры / полигоны.
    """

    user = models.ForeignKey(
        'account.User',
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name='mode_switch_logs',
        verbose_name='Пользователь',
    )
    region_slug = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='Slug региона',
    )
    mode_from = models.CharField(
        max_length=20,
        verbose_name='Режим ДО',
    )
    mode_to = models.CharField(
        max_length=20,
        verbose_name='Режим ПОСЛЕ',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Создано',
    )

    class Meta:
        verbose_name = 'Переключение режима отображения'
        verbose_name_plural = 'Переключения режима отображения'
        indexes = [
            models.Index(fields=['region_slug', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['mode_to', 'mode_from', 'created_at']),
        ]

    def __str__(self) -> str:
        user_str = self.user.username if self.user else 'anonymous'
        return f'{user_str}: {self.mode_from} → {self.mode_to} ({self.region_slug})'
