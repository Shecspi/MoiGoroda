# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

import pytest
from django.conf import settings
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

    assert cache_config['BACKEND'] == 'django_redis.cache.RedisCache'
    assert cache_config['LOCATION'] == 'redis://redis:6379/9'
    assert cache_config['OPTIONS']['CLIENT_CLASS'] == 'django_redis.client.DefaultClient'
    assert cache_config['OPTIONS']['SOCKET_CONNECT_TIMEOUT'] == 1
    assert cache_config['OPTIONS']['SOCKET_TIMEOUT'] == 1
    assert cache_config['OPTIONS']['IGNORE_EXCEPTIONS'] is True


@pytest.mark.unit
def test_cache_logger_uses_formatter_without_request_fields() -> None:
    """DEBUG-логи cache helper'ов не должны требовать поля request-контекста."""
    logging_settings = cast(dict[str, Any], settings.LOGGING)
    cache_handler = logging_settings['loggers']['services.cache']['handlers'][0]
    formatter_name = logging_settings['handlers'][cache_handler]['formatter']
    formatter_format = logging_settings['formatters'][formatter_name]['format']

    record = LogRecord(
        name='services.cache',
        level=10,
        pathname=__file__,
        lineno=1,
        msg='Cache miss: %s',
        args=('test-key',),
        exc_info=None,
    )

    assert '%(IP)' not in formatter_format
    assert '%(user)' not in formatter_format
    assert Formatter(formatter_format).format(record).endswith('Cache miss: test-key')
