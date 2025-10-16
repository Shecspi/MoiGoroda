"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from typing import Any


# Общие фикстуры для всех тестов приложения services


@pytest.fixture
def sample_request() -> dict[str, Any]:
    """Фикстура с тестовым request"""
    return {
        'path': '/test/path/',
        'user': 'testuser',
        'ip': '127.0.0.1',
    }


@pytest.fixture
def test_country() -> Any:
    """Фикстура с тестовой страной"""
    from country.models import Country

    return Country.objects.create(name='Test Country', code='TC')


@pytest.fixture
def test_region_type() -> Any:
    """Фикстура с тестовым типом региона"""
    from region.models import RegionType

    return RegionType.objects.create(title='область')


@pytest.fixture
def test_region(test_country: Any, test_region_type: Any) -> Any:
    """Фикстура с тестовым регионом"""
    from region.models import Region

    return Region.objects.create(
        title='Test Region', country=test_country, type=test_region_type, iso3166='TC-TR'
    )


@pytest.fixture
def test_city(test_region: Any, test_country: Any) -> Any:
    """Фикстура с тестовым городом"""
    from city.models import City

    return City.objects.create(
        title='Test City',
        region=test_region,
        country=test_country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )
