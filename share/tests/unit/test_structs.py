"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import pytest

from share.structs import TypeOfSharedPage


@pytest.mark.unit
def test_type_of_shared_page_enum_values() -> None:
    """Тест значений enum TypeOfSharedPage"""
    assert TypeOfSharedPage.dashboard == 'dashboard'
    assert TypeOfSharedPage.city_map == 'city_map'
    assert TypeOfSharedPage.region_map == 'region_map'


@pytest.mark.unit
def test_type_of_shared_page_enum_members() -> None:
    """Тест членов enum TypeOfSharedPage"""
    assert hasattr(TypeOfSharedPage, 'dashboard')
    assert hasattr(TypeOfSharedPage, 'city_map')
    assert hasattr(TypeOfSharedPage, 'region_map')


@pytest.mark.unit
def test_type_of_shared_page_enum_count() -> None:
    """Тест количества членов enum TypeOfSharedPage"""
    assert len(TypeOfSharedPage) == 3


@pytest.mark.unit
def test_type_of_shared_page_enum_iteration() -> None:
    """Тест итерации по enum TypeOfSharedPage"""
    members = list(TypeOfSharedPage)
    assert len(members) == 3
    assert TypeOfSharedPage.dashboard in members
    assert TypeOfSharedPage.city_map in members
    assert TypeOfSharedPage.region_map in members
