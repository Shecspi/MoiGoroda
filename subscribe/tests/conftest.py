"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from city.models import City
from country.models import Country
from region.models import Region, RegionType


@pytest.fixture
def test_country() -> Country:
    """Создаёт тестовую страну"""
    return Country.objects.create(name='Тестовая страна', code='TC')


@pytest.fixture
def test_region_type() -> RegionType:
    """Создаёт тестовый тип региона"""
    return RegionType.objects.create(title='Область')


@pytest.fixture
def test_region(test_country: Country, test_region_type: RegionType) -> Region:
    """Создаёт тестовый регион"""
    return Region.objects.create(
        title='Тестовый регион',
        full_name='Тестовый регион полное название',
        country=test_country,
        type=test_region_type,
        iso3166='TEST',
    )


@pytest.fixture
def test_city(test_country: Country, test_region: Region) -> City:
    """Создаёт тестовый город"""
    return City.objects.create(
        title='Тестовый город',
        region=test_region,
        country=test_country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )
