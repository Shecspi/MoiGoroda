# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from typing import Any

import pytest
from django.core.cache import caches

from services.cache import delete_cache, get_or_set_cache

stats_cache = caches['stats']


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    caches['default'].clear()
    stats_cache.clear()


@pytest.mark.unit
def test_get_or_set_cache_calls_factory_on_miss(mocker: Any) -> None:
    factory = mocker.Mock(return_value={'value': 1})

    result = get_or_set_cache('test-key', ttl_seconds=60, factory=factory)

    assert result == {'value': 1}
    assert stats_cache.get('test-key') == {'value': 1}
    factory.assert_called_once_with()


@pytest.mark.unit
def test_get_or_set_cache_returns_cached_value_without_factory(
    mocker: Any,
) -> None:
    stats_cache.set('test-key', {'value': 1}, timeout=60)
    factory = mocker.Mock(return_value={'value': 2})
    logger_debug = mocker.patch('services.cache.logger.debug')

    result = get_or_set_cache('test-key', ttl_seconds=60, factory=factory)

    assert result == {'value': 1}
    factory.assert_not_called()
    logger_debug.assert_called_once_with('Cache hit: %s', 'test-key')


@pytest.mark.unit
def test_get_or_set_cache_logs_miss_and_set(
    mocker: Any,
) -> None:
    factory = mocker.Mock(return_value={'value': 1})
    logger_debug = mocker.patch('services.cache.logger.debug')

    get_or_set_cache('test-key', ttl_seconds=60, factory=factory)

    logger_debug.assert_has_calls(
        [
            mocker.call('Cache miss: %s', 'test-key'),
            mocker.call('Cache set: %s ttl=%s', 'test-key', 60),
        ]
    )


@pytest.mark.unit
def test_delete_cache_removes_cached_value(mocker: Any) -> None:
    stats_cache.set('test-key', {'value': 1}, timeout=60)
    logger_debug = mocker.patch('services.cache.logger.debug')

    delete_cache('test-key')

    assert stats_cache.get('test-key') is None
    logger_debug.assert_called_once_with('Cache delete: %s', 'test-key')


@pytest.mark.unit
def test_cache_helpers_do_not_write_to_default_cache(mocker: Any) -> None:
    factory = mocker.Mock(return_value={'value': 1})

    get_or_set_cache('test-key', ttl_seconds=60, factory=factory)

    assert caches['default'].get('test-key') is None
    assert stats_cache.get('test-key') == {'value': 1}
