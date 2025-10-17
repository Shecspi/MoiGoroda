"""
Unit-тесты для модели FavoriteCollection.
Тесты проверяют структуру модели без обращения к базе данных.
"""

import pytest

from collection.models import FavoriteCollection


@pytest.mark.unit
class TestFavoriteCollectionModel:
    """Unit-тесты для структуры модели FavoriteCollection (без БД)."""

    def test_model_has_required_fields(self) -> None:
        """Проверяет наличие необходимых полей в модели."""
        # Проверяем что модель имеет нужные поля
        assert hasattr(FavoriteCollection, 'user')
        assert hasattr(FavoriteCollection, 'collection')
        assert hasattr(FavoriteCollection, 'created_at')

    def test_meta_options(self) -> None:
        """Проверяет настройки Meta модели."""
        meta = FavoriteCollection._meta

        # Проверяем ordering
        assert meta.ordering == ['-created_at']

        # Проверяем verbose_name
        assert meta.verbose_name == 'Избранная коллекция'
        assert meta.verbose_name_plural == 'Избранные коллекции'

        # Проверяем unique_together
        assert ('user', 'collection') in meta.unique_together
