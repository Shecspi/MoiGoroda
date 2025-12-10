"""
Юнит-тесты для репозитория персональных коллекций.
"""

import pytest

from collection.repository import CollectionRepository


@pytest.mark.unit
class TestCollectionRepository:
    """Тесты для CollectionRepository."""

    def test_repository_initialization(self) -> None:
        """Проверяет инициализацию репозитория."""
        repository = CollectionRepository()
        assert repository is not None

    def test_repository_has_get_personal_collections_with_annotations_method(
        self,
    ) -> None:
        """Проверяет наличие метода get_personal_collections_with_annotations."""
        repository = CollectionRepository()
        assert hasattr(repository, 'get_personal_collections_with_annotations')
        assert callable(repository.get_personal_collections_with_annotations)

    def test_repository_has_get_personal_collection_by_id_method(self) -> None:
        """Проверяет наличие метода get_personal_collection_by_id."""
        repository = CollectionRepository()
        assert hasattr(repository, 'get_personal_collection_by_id')
        assert callable(repository.get_personal_collection_by_id)

    def test_repository_has_get_public_collections_with_annotations_method(
        self,
    ) -> None:
        """Проверяет наличие метода get_public_collections_with_annotations."""
        repository = CollectionRepository()
        assert hasattr(repository, 'get_public_collections_with_annotations')
        assert callable(repository.get_public_collections_with_annotations)
