"""
Общие фикстуры для тестов country.
"""

import pytest
from django.contrib.auth.models import User

from country.models import Country, PartOfTheWorld, Location
from region.models import RegionType


@pytest.fixture
def region_type() -> RegionType:
    """Создает тип региона для тестов."""
    return RegionType.objects.get_or_create(title='город федерального значения')[0]


@pytest.fixture
def part_of_the_world() -> PartOfTheWorld:
    """Создает часть света для тестов."""
    return PartOfTheWorld.objects.get_or_create(name='Европа')[0]


@pytest.fixture
def location(part_of_the_world: PartOfTheWorld) -> Location:
    """Создает расположение для тестов."""
    return Location.objects.get_or_create(
        name='Восточная Европа', part_of_the_world=part_of_the_world
    )[0]


@pytest.fixture
def user() -> User:
    """Создает тестового пользователя."""
    return User.objects.create_user(username='testuser', password='testpass')
