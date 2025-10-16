"""
Юнит-тесты для админки приложения collection.
"""

import pytest
from django.contrib import admin

from collection.models import Collection


@pytest.mark.unit
class TestCollectionAdmin:
    """Тесты для админки Collection."""

    def test_collection_registered_in_admin(self) -> None:
        """Проверяет что модель Collection зарегистрирована в админке."""
        assert Collection in admin.site._registry

    def test_collection_admin_site_exists(self) -> None:
        """Проверяет что для Collection есть админ-сайт."""
        admin_instance = admin.site._registry.get(Collection)
        assert admin_instance is not None

    def test_collection_admin_default_fields(self) -> None:
        """Проверяет стандартные поля админки."""
        admin_instance = admin.site._registry.get(Collection)
        # Проверяем что это экземпляр ModelAdmin
        assert isinstance(admin_instance, admin.ModelAdmin)
