"""
Запись и нормализация источника добавления посещённого города.
"""

from __future__ import annotations

import logging

from django.db import IntegrityError, transaction

from analytics.models import VisitedCityAddSource
from city.models import VisitedCity

logger = logging.getLogger(__name__)

_RAW_HINT_MAX = VisitedCityAddSource._meta.get_field('raw_hint').max_length

_ALLOWED_HTML_SURFACES = frozenset(
    s.value
    for s in VisitedCityAddSource.Surface
    if s
    not in (
        VisitedCityAddSource.Surface.API_UNKNOWN,
        VisitedCityAddSource.Surface.UNKNOWN,
    )
)

# Строка от клиента (API `from`, старые значения) → Surface
_FROM_RAW_TO_SURFACE: dict[str, VisitedCityAddSource.Surface] = {
    'sidebar': VisitedCityAddSource.Surface.SIDEBAR,
    'city_list': VisitedCityAddSource.Surface.CITY_LIST,
    'city_page': VisitedCityAddSource.Surface.CITY_PAGE,
    'visited_cities_map': VisitedCityAddSource.Surface.VISITED_CITIES_MAP,
    'region_map': VisitedCityAddSource.Surface.REGION_MAP,
    'collection_personal_map': VisitedCityAddSource.Surface.COLLECTION_PERSONAL_MAP,
    'collection_selected_map': VisitedCityAddSource.Surface.COLLECTION_SELECTED_MAP,
    # Исторические / человекочитаемые значения
    'general map': VisitedCityAddSource.Surface.VISITED_CITIES_MAP,
    'unknown location': VisitedCityAddSource.Surface.API_UNKNOWN,
}


def normalize_html_surface(raw: str | None) -> VisitedCityAddSource.Surface:
    if not raw or not str(raw).strip():
        return VisitedCityAddSource.Surface.UNKNOWN

    key = str(raw).strip()
    if key in _ALLOWED_HTML_SURFACES:
        return VisitedCityAddSource.Surface(key)

    return VisitedCityAddSource.Surface.UNKNOWN


def normalize_api_from_raw(raw: str | None) -> tuple[VisitedCityAddSource.Surface, str]:
    if raw is None:
        return VisitedCityAddSource.Surface.API_UNKNOWN, ''
    stripped = str(raw).strip()
    if not stripped:
        return VisitedCityAddSource.Surface.API_UNKNOWN, ''
    key = stripped.lower()
    surface = _FROM_RAW_TO_SURFACE.get(key)
    if surface is not None:
        redundant = stripped.lower() == surface.value.lower()
        return surface, '' if redundant else stripped[:_RAW_HINT_MAX]
    # Точное совпадение с enum value (клиент шлёт snake_case)
    if stripped in _ALLOWED_HTML_SURFACES:
        return VisitedCityAddSource.Surface(stripped), ''
    return VisitedCityAddSource.Surface.API_UNKNOWN, stripped[:_RAW_HINT_MAX]


def record_visited_city_add(
    *,
    visited_city: VisitedCity,
    surface: VisitedCityAddSource.Surface,
    raw_hint: str = '',
) -> None:
    hint = (raw_hint or '')[:_RAW_HINT_MAX]

    try:
        with transaction.atomic():
            VisitedCityAddSource.objects.create(
                visited_city=visited_city,
                surface=surface,
                raw_hint=hint,
            )
    except IntegrityError:
        logger.warning(
            'VisitedCityAddSource duplicate skipped for visited_city_id=%s',
            visited_city.pk,
        )
