"""
Юнит-тесты для админки приложения country.
"""

import pytest
from django.contrib import admin

from country.models import Country, VisitedCountry, PartOfTheWorld, Location
from country.admin import CountryAdmin, VisitedCountryAdmin


@pytest.mark.unit
class TestCountryAdmin:
    """Тесты для админки Country."""

    def test_country_registered_in_admin(self) -> None:
        """Проверяет что модель Country зарегистрирована в админке."""
        assert Country in admin.site._registry

    def test_country_admin_list_display(self) -> None:
        """Проверяет list_display для Country."""
        admin_instance = admin.site._registry.get(Country)
        assert isinstance(admin_instance, CountryAdmin)
        expected_fields = ('id', 'name', 'fullname', 'code', 'location', 'is_member_of_un', 'owner')
        assert admin_instance.list_display == expected_fields

    def test_country_admin_search_fields(self) -> None:
        """Проверяет search_fields для Country."""
        admin_instance = admin.site._registry.get(Country)
        assert admin_instance is not None
        assert admin_instance.search_fields == ('name', 'fullname', 'code')


@pytest.mark.unit
class TestVisitedCountryAdmin:
    """Тесты для админки VisitedCountry."""

    def test_visited_country_registered_in_admin(self) -> None:
        """Проверяет что модель VisitedCountry зарегистрирована в админке."""
        assert VisitedCountry in admin.site._registry

    def test_visited_country_admin_list_display(self) -> None:
        """Проверяет list_display для VisitedCountry."""
        admin_instance = admin.site._registry.get(VisitedCountry)
        assert isinstance(admin_instance, VisitedCountryAdmin)
        expected_fields = ('id', 'country', 'location', 'part_of_the_world', 'user')
        assert admin_instance.list_display == expected_fields

    def test_visited_country_admin_ordering(self) -> None:
        """Проверяет ordering для VisitedCountry."""
        admin_instance = admin.site._registry.get(VisitedCountry)
        assert admin_instance is not None
        assert admin_instance.ordering == ('country', 'user')


@pytest.mark.unit
class TestOtherModelsAdmin:
    """Тесты для админки других моделей."""

    def test_part_of_the_world_registered(self) -> None:
        """Проверяет что PartOfTheWorld зарегистрирована."""
        assert PartOfTheWorld in admin.site._registry

    def test_location_registered(self) -> None:
        """Проверяет что Location зарегистрирована."""
        assert Location in admin.site._registry
