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


@pytest.mark.unit
def test_tests_use_local_memory_cache_backend() -> None:
    """Тестовая среда не должна зависеть от внешнего Redis."""
    assert settings.TESTING is True
    assert settings.CACHES['default']['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache'


@pytest.mark.unit
def test_sessions_use_database_backed_cache_backend() -> None:
    """Сессии не должны теряться при очистке cache backend."""
    assert settings.SESSION_ENGINE == 'django.contrib.sessions.backends.cached_db'


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
