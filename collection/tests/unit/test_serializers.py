"""
Юнит-тесты для сериализаторов приложения collection.
"""

from typing import Any

import pytest
from rest_framework.exceptions import ValidationError

from collection.serializers import (
    CollectionSearchParamsSerializer,
    PersonalCollectionCreateSerializer,
    PersonalCollectionUpdatePublicStatusSerializer,
    PersonalCollectionUpdateSerializer,
)


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


@pytest.mark.unit
class TestPersonalCollectionCreateSerializer:
    """Тесты для PersonalCollectionCreateSerializer."""

    def test_serializer_with_valid_data(self) -> None:
        """Проверяет валидацию с корректными данными."""
        data = {'title': 'Моя коллекция', 'city_ids': [1, 2, 3]}
        serializer = PersonalCollectionCreateSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['title'] == 'Моя коллекция'
        assert serializer.validated_data['city_ids'] == [1, 2, 3]
        assert serializer.validated_data.get('is_public') is False

    def test_serializer_with_is_public_true(self) -> None:
        """Проверяет валидацию с is_public=True."""
        data = {'title': 'Публичная коллекция', 'city_ids': [1, 2], 'is_public': True}
        serializer = PersonalCollectionCreateSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['is_public'] is True

    def test_serializer_without_title(self) -> None:
        """Проверяет валидацию без title."""
        data = {'city_ids': [1, 2, 3]}
        serializer = PersonalCollectionCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_serializer_without_city_ids(self) -> None:
        """Проверяет валидацию без city_ids."""
        data = {'title': 'Коллекция'}
        serializer = PersonalCollectionCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'city_ids' in serializer.errors

    def test_serializer_with_empty_city_ids(self) -> None:
        """Проверяет валидацию с пустым city_ids."""
        data = {'title': 'Коллекция', 'city_ids': []}
        serializer = PersonalCollectionCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'city_ids' in serializer.errors

    def test_serializer_with_long_title(self) -> None:
        """Проверяет валидацию с длинным title."""
        long_title = 'a' * 257  # Превышает max_length=256
        data = {'title': long_title, 'city_ids': [1]}
        serializer = PersonalCollectionCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_serializer_with_max_length_title(self) -> None:
        """Проверяет валидацию с максимальной длиной title."""
        max_title = 'a' * 256
        data = {'title': max_title, 'city_ids': [1]}
        serializer = PersonalCollectionCreateSerializer(data=data)
        assert serializer.is_valid()

    def test_serializer_with_invalid_city_ids_type(self) -> None:
        """Проверяет валидацию с неверным типом city_ids."""
        data = {'title': 'Коллекция', 'city_ids': 'not_a_list'}
        serializer = PersonalCollectionCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'city_ids' in serializer.errors

    def test_serializer_with_non_integer_city_ids(self) -> None:
        """Проверяет валидацию с нецелочисленными city_ids."""
        data = {'title': 'Коллекция', 'city_ids': [1, 'not_int', 3]}
        serializer = PersonalCollectionCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'city_ids' in serializer.errors


@pytest.mark.unit
class TestPersonalCollectionUpdateSerializer:
    """Тесты для PersonalCollectionUpdateSerializer."""

    def test_serializer_with_valid_data(self) -> None:
        """Проверяет валидацию с корректными данными."""
        data = {'title': 'Обновленная коллекция', 'city_ids': [1, 2, 3, 4]}
        serializer = PersonalCollectionUpdateSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['title'] == 'Обновленная коллекция'
        assert serializer.validated_data['city_ids'] == [1, 2, 3, 4]
        assert serializer.validated_data.get('is_public') is False

    def test_serializer_without_title(self) -> None:
        """Проверяет валидацию без title."""
        data = {'city_ids': [1, 2]}
        serializer = PersonalCollectionUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_serializer_without_city_ids(self) -> None:
        """Проверяет валидацию без city_ids."""
        data = {'title': 'Коллекция'}
        serializer = PersonalCollectionUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'city_ids' in serializer.errors

    def test_serializer_with_empty_city_ids(self) -> None:
        """Проверяет валидацию с пустым city_ids."""
        data = {'title': 'Коллекция', 'city_ids': []}
        serializer = PersonalCollectionUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'city_ids' in serializer.errors


@pytest.mark.unit
class TestPersonalCollectionUpdatePublicStatusSerializer:
    """Тесты для PersonalCollectionUpdatePublicStatusSerializer."""

    def test_serializer_with_valid_data_true(self) -> None:
        """Проверяет валидацию с is_public=True."""
        data = {'is_public': True}
        serializer = PersonalCollectionUpdatePublicStatusSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['is_public'] is True

    def test_serializer_with_valid_data_false(self) -> None:
        """Проверяет валидацию с is_public=False."""
        data = {'is_public': False}
        serializer = PersonalCollectionUpdatePublicStatusSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['is_public'] is False

    def test_serializer_without_is_public(self) -> None:
        """Проверяет валидацию без is_public."""
        data: dict[str, Any] = {}
        serializer = PersonalCollectionUpdatePublicStatusSerializer(data=data)
        assert not serializer.is_valid()
        assert 'is_public' in serializer.errors

    def test_serializer_with_invalid_is_public_type(self) -> None:
        """Проверяет валидацию с неверным типом is_public."""
        data = {'is_public': 'not_boolean'}
        serializer = PersonalCollectionUpdatePublicStatusSerializer(data=data)
        assert not serializer.is_valid()
        assert 'is_public' in serializer.errors
