"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

import pytest
from django.contrib import admin

from city.models import City
from region.admin import AreaAdmin, RegionTypeAdmin, RegionAdmin
from region.models import Area, RegionType, Region


@pytest.mark.unit
class TestAreaAdmin:
    """Тесты для AreaAdmin"""

    def test_area_admin_registered(self) -> None:
        """Тест что AreaAdmin зарегистрирован в админке"""
        assert admin.site.is_registered(Area)

    def test_area_admin_list_display(self) -> None:
        """Тест настройки list_display"""
        admin_instance = AreaAdmin(Area, admin.site)
        assert admin_instance.list_display == ('title', 'get_qty_of_regions', 'get_qty_of_cities')

    @pytest.mark.django_db
    def test_get_qty_of_regions(
        self, test_country: Any, test_region_type: Any, test_area: Area
    ) -> None:
        """Тест метода get_qty_of_regions"""
        Region.objects.create(
            title='Region1',
            full_name='Region 1',
            country=test_country,
            type=test_region_type,
            area=test_area,
            iso3166='RU-R1',
        )

        admin_instance = AreaAdmin(Area, admin.site)
        count = admin_instance.get_qty_of_regions(test_area)
        assert count >= 1

    @pytest.mark.django_db
    def test_get_qty_of_cities(
        self,
        test_country: Any,
        test_region_type: Any,
        test_area: Area,
        test_region: Region,
        test_city: City,
    ) -> None:
        """Тест метода get_qty_of_cities"""
        admin_instance = AreaAdmin(Area, admin.site)
        count = admin_instance.get_qty_of_cities(test_area)
        assert count >= 1


@pytest.mark.unit
class TestRegionTypeAdmin:
    """Тесты для RegionTypeAdmin"""

    def test_region_type_admin_registered(self) -> None:
        """Тест что RegionTypeAdmin зарегистрирован в админке"""
        assert admin.site.is_registered(RegionType)

    def test_region_type_admin_fields(self) -> None:
        """Тест настройки fields"""
        admin_instance = RegionTypeAdmin(RegionType, admin.site)
        assert admin_instance.fields == ('title',)


@pytest.mark.unit
class TestRegionAdmin:
    """Тесты для RegionAdmin"""

    def test_region_admin_registered(self) -> None:
        """Тест что RegionAdmin зарегистрирован в админке"""
        assert admin.site.is_registered(Region)

    def test_region_admin_fields(self) -> None:
        """Тест настройки fields"""
        admin_instance = RegionAdmin(Region, admin.site)
        assert admin_instance.fields == ['country', 'area', 'title', 'type', 'full_name', 'iso3166']

    def test_region_admin_list_display(self) -> None:
        """Тест настройки list_display"""
        admin_instance = RegionAdmin(Region, admin.site)
        assert admin_instance.list_display == (
            'id',
            'get_title',
            'get_qty_of_cities',
            'country',
            'area',
            'iso3166',
        )

    def test_region_admin_search_fields(self) -> None:
        """Тест настройки search_fields"""
        admin_instance = RegionAdmin(Region, admin.site)
        assert admin_instance.search_fields == ('title',)

    @pytest.mark.django_db
    def test_get_title_returns_region_object(self, test_region: Region) -> None:
        """Тест что get_title возвращает объект региона"""
        admin_instance = RegionAdmin(Region, admin.site)
        title = admin_instance.get_title(test_region)
        assert title == test_region
        assert str(title) == test_region.full_name

    @pytest.mark.django_db
    def test_get_qty_of_cities(self, test_region: Region, test_city: City) -> None:
        """Тест метода get_qty_of_cities"""
        admin_instance = RegionAdmin(Region, admin.site)
        count = admin_instance.get_qty_of_cities(test_region)
        assert count >= 1
