"""
Юнит-тесты для сервиса персональных коллекций.
"""

import pytest

from collection.services import PersonalCollectionService


@pytest.mark.unit
class TestPersonalCollectionService:
    """Тесты для PersonalCollectionService."""

    def test_service_initialization(self) -> None:
        """Проверяет инициализацию сервиса."""
        service = PersonalCollectionService()
        assert service is not None
        assert service.repository is not None

    def test_service_initialization_with_repository(self) -> None:
        """Проверяет инициализацию сервиса с переданным репозиторием."""
        from collection.repository import CollectionRepository

        repository = CollectionRepository()
        service = PersonalCollectionService(repository=repository)
        assert service.repository == repository

    def test_service_has_get_collection_with_access_check_method(self) -> None:
        """Проверяет наличие метода get_collection_with_access_check."""
        service = PersonalCollectionService()
        assert hasattr(service, 'get_collection_with_access_check')
        assert callable(service.get_collection_with_access_check)

    def test_service_has_get_cities_for_collection_method(self) -> None:
        """Проверяет наличие метода get_cities_for_collection."""
        service = PersonalCollectionService()
        assert hasattr(service, 'get_cities_for_collection')
        assert callable(service.get_cities_for_collection)

    def test_service_has_get_list_context_data_method(self) -> None:
        """Проверяет наличие метода get_list_context_data."""
        service = PersonalCollectionService()
        assert hasattr(service, 'get_list_context_data')
        assert callable(service.get_list_context_data)

    def test_service_has_get_map_context_data_method(self) -> None:
        """Проверяет наличие метода get_map_context_data."""
        service = PersonalCollectionService()
        assert hasattr(service, 'get_map_context_data')
        assert callable(service.get_map_context_data)
