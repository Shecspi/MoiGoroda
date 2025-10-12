"""
Юнит-тесты для сериализаторов приложения collection.
"""

from typing import Any

import pytest
from rest_framework.exceptions import ValidationError

from collection.serializers import CollectionSearchParamsSerializer


@pytest.mark.unit
class TestCollectionSearchParamsSerializer:
    """Тесты для CollectionSearchParamsSerializer."""

    def test_serializer_with_valid_data(self) -> None:
        """Проверяет валидацию с корректными данными."""
        data = {'query': 'тест'}
        serializer = CollectionSearchParamsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['query'] == 'тест'

    def test_serializer_with_empty_query(self) -> None:
        """Проверяет валидацию с пустым query (не валидно)."""
        data = {'query': ''}
        serializer = CollectionSearchParamsSerializer(data=data)
        assert not serializer.is_valid()
        assert 'query' in serializer.errors

    def test_serializer_without_query(self) -> None:
        """Проверяет валидацию без параметра query."""
        data: dict[str, Any] = {}
        serializer = CollectionSearchParamsSerializer(data=data)
        assert not serializer.is_valid()
        assert 'query' in serializer.errors

    def test_serializer_query_field_is_required(self) -> None:
        """Проверяет что поле query обязательное."""
        data: dict[str, Any] = {}
        serializer = CollectionSearchParamsSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_serializer_with_long_query(self) -> None:
        """Проверяет валидацию с длинным query."""
        long_query = 'a' * 1000
        data = {'query': long_query}
        serializer = CollectionSearchParamsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['query'] == long_query

    def test_serializer_with_special_characters(self) -> None:
        """Проверяет валидацию со спецсимволами."""
        data = {'query': '!@#$%^&*()'}
        serializer = CollectionSearchParamsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['query'] == '!@#$%^&*()'
