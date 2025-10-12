"""
Общие фикстуры для тестов коллекций.
"""

import pytest

from region.models import RegionType


@pytest.fixture
def region_type() -> RegionType:
    """Создает тип региона для тестов."""
    return RegionType.objects.get_or_create(title='город федерального значения')[0]
