# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""Общие helper-функции для cache-aside сценариев."""

from collections.abc import Callable
import logging
from typing import TypeVar, cast

from django.core.cache import cache

T = TypeVar('T')
logger = logging.getLogger(__name__)


def get_or_set_cache(key: str, ttl_seconds: int, factory: Callable[[], T]) -> T:
    """
    Возвращает значение из кеша или вычисляет и сохраняет его через factory.

    Factory вызывается только при cache miss. Значение `None` считается отсутствием кеша,
    поэтому для кеширования пустых результатов лучше использовать пустые коллекции.
    """
    cached = cache.get(key)
    if cached is not None:
        logger.debug('Cache hit: %s', key)
        return cast(T, cached)

    logger.debug('Cache miss: %s', key)
    value = factory()
    cache.set(key, value, timeout=ttl_seconds)
    logger.debug('Cache set: %s ttl=%s', key, ttl_seconds)
    return value


def delete_cache(key: str) -> None:
    """Удаляет значение из кеша по ключу."""
    cache.delete(key)
    logger.debug('Cache delete: %s', key)
