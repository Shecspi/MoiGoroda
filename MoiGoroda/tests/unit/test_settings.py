# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

import pytest
from django.conf import settings


@pytest.mark.unit
def test_tests_use_local_memory_cache_backend() -> None:
    """Тестовая среда не должна зависеть от внешнего Redis."""
    assert settings.TESTING is True
    assert settings.CACHES['default']['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache'
