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
