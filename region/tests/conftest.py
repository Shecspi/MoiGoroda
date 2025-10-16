"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest
from django.contrib.auth.models import User

from city.models import City
from country.models import Country
from region.models import Region, RegionType, Area


@pytest.fixture
def test_country() -> Country:
    """Создаёт тестовую страну"""
    return Country.objects.create(name='Россия', code='RU')


@pytest.fixture
def test_region_type() -> RegionType:
    """Создаёт тестовый тип региона"""
    return RegionType.objects.create(title='Область')


@pytest.fixture
def test_area(test_country: Country) -> Area:
    """Создаёт тестовый федеральный округ"""
    return Area.objects.create(title='Центральный федеральный округ', country=test_country)


@pytest.fixture
def test_region(test_country: Country, test_region_type: RegionType, test_area: Area) -> Region:
    """Создаёт тестовый регион"""
    return Region.objects.create(
        title='Московская',
        full_name='Московская область',
        country=test_country,
        type=test_region_type,
        area=test_area,
        iso3166='RU-MOS',
    )


@pytest.fixture
def test_city(test_country: Country, test_region: Region) -> City:
    """Создаёт тестовый город"""
    return City.objects.create(
        title='Москва',
        region=test_region,
        country=test_country,
        coordinate_width=55.7558,
        coordinate_longitude=37.6173,
    )


@pytest.fixture
def test_user() -> User:
    """Создаёт тестового пользователя"""
    return User.objects.create_user(username='testuser', password='testpass123')
