# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from importlib import reload

import pytest
from django.conf import settings
from django.utils.module_loading import import_string
from logging import Formatter
from logging import LogRecord
from typing import Any, cast

from MoiGoroda import settings as project_settings


@pytest.mark.unit
def test_tests_use_local_memory_cache_backend() -> None:
    """Тестовая среда не должна зависеть от внешнего Redis."""
    assert settings.TESTING is True
    assert settings.CACHES['default']['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache'
    assert settings.CACHES['sessions']['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache'
    assert settings.CACHES['stats']['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache'


@pytest.mark.unit
def test_sessions_use_database_backed_cache_backend() -> None:
    """Сессии не должны теряться при очистке cache backend."""
    assert settings.SESSION_ENGINE == 'django.contrib.sessions.backends.cached_db'
    assert settings.SESSION_CACHE_ALIAS == 'sessions'


@pytest.mark.unit
def test_redis_cache_config_sets_timeouts_and_optional_exception_policy() -> None:
    """Redis cache должен быстро отдавать ошибку и явно задавать failure policy."""
    cache_config = project_settings.build_redis_cache_config(
        location='redis://redis:6379/9',
        ignore_exceptions=True,
    )

    assert cache_config['BACKEND'] == 'django_prometheus.cache.backends.redis.RedisCache'
    assert cache_config['LOCATION'] == 'redis://redis:6379/9'
    cache_options = cast(dict[str, Any], cache_config['OPTIONS'])
    assert cache_options['CLIENT_CLASS'] == 'django_redis.client.DefaultClient'
    assert cache_options['SOCKET_CONNECT_TIMEOUT'] == 1
    assert cache_options['SOCKET_TIMEOUT'] == 1
    assert cache_options['IGNORE_EXCEPTIONS'] is True


@pytest.mark.unit
def test_redis_socket_timeout_seconds_uses_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Redis socket timeout должен настраиваться через переменные окружения."""
    monkeypatch.setenv('REDIS_SOCKET_TIMEOUT_SECONDS', '0.5')
    reloaded_settings = reload(project_settings)

    try:
        cache_config = reloaded_settings.build_redis_cache_config(location='redis://redis:6379/9')

        assert reloaded_settings.REDIS_SOCKET_TIMEOUT_SECONDS == 0.5
        assert cache_config['OPTIONS']['SOCKET_CONNECT_TIMEOUT'] == 0.5
        assert cache_config['OPTIONS']['SOCKET_TIMEOUT'] == 0.5
    finally:
        reload(project_settings)


@pytest.mark.unit
def test_cache_logger_uses_formatter_without_request_fields() -> None:
    """DEBUG-логи cache helper'ов используют общий формат с fallback-контекстом."""
    logging_settings = cast(dict[str, Any], settings.LOGGING)
    cache_handler = logging_settings['loggers']['services.cache']['handlers'][0]
    cache_handler_config = logging_settings['handlers'][cache_handler]
    cache_filters = cache_handler_config['filters']
    formatter_name = logging_settings['handlers'][cache_handler]['formatter']
    formatter_format = logging_settings['formatters'][formatter_name]['format']
    log_filter_class = import_string(logging_settings['filters']['add_default_log_context']['()'])
    log_filter = log_filter_class()

    record = LogRecord(
        name='services.cache',
        level=10,
        pathname=__file__,
        lineno=1,
        msg='Cache miss: %s',
        args=('test-key',),
        exc_info=None,
    )

    assert formatter_name == 'detail_app'
    assert 'add_default_log_context' in cache_filters
    assert '%(IP)' in formatter_format
    assert '%(user)' in formatter_format

    assert log_filter.filter(record) is True
    formatted_record = Formatter(formatter_format).format(record)

    assert 'INTERNAL' in formatted_record
    assert 'CACHE' in formatted_record
    assert formatted_record.endswith('Cache miss: test-key')
