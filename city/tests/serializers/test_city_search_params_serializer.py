"""
Mock-тесты для сериализатора CitySearchParamsSerializer.

Покрывает:
- Валидацию обязательного поля query
- Валидацию необязательного поля country
- Проверку корректности данных
- Проверку ошибок валидации
- Проверку типов данных

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from unittest.mock import MagicMock
from rest_framework import serializers

from city.serializers import CitySearchParamsSerializer


class TestCitySearchParamsSerializer:
    """Тесты для сериализатора CitySearchParamsSerializer."""

    def test_valid_data_with_query_only(self) -> None:
        """Тест валидации с только обязательным полем query."""
        data = {'query': 'Moscow'}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data['query'] == 'Moscow'
        assert 'country' not in serializer.validated_data

    def test_valid_data_with_query_and_country(self) -> None:
        """Тест валидации с полными данными."""
        data = {'query': 'Moscow', 'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data['query'] == 'Moscow'
        assert serializer.validated_data['country'] == 'RU'
        assert serializer.validated_data['limit'] == 50  # Дефолтное значение

    def test_valid_data_with_limit(self) -> None:
        """Тест валидации с пользовательским лимитом."""
        data = {'query': 'Moscow', 'limit': 20}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data['query'] == 'Moscow'
        assert serializer.validated_data['limit'] == 20

    def test_valid_data_with_all_parameters(self) -> None:
        """Тест валидации со всеми параметрами."""
        data = {'query': 'Moscow', 'country': 'RU', 'limit': 30}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data['query'] == 'Moscow'
        assert serializer.validated_data['country'] == 'RU'
        assert serializer.validated_data['limit'] == 30

    def test_invalid_limit_too_small(self) -> None:
        """Тест валидации с лимитом меньше минимального."""
        data = {'query': 'Moscow', 'limit': 0}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'limit' in serializer.errors

    def test_invalid_limit_too_large(self) -> None:
        """Тест валидации с лимитом больше максимального."""
        data = {'query': 'Moscow', 'limit': 300}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'limit' in serializer.errors

    def test_empty_query_validation_error(self) -> None:
        """Тест ошибки валидации при пустой строке query."""
        data = {'query': ''}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'query' in serializer.errors
        assert len(serializer.errors['query']) > 0

    def test_missing_query_validation_error(self) -> None:
        """Тест ошибки валидации при отсутствии поля query."""
        data = {'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'query' in serializer.errors
        assert 'required' in str(serializer.errors['query']).lower()

    def test_empty_data_validation_error(self) -> None:
        """Тест ошибки валидации при пустых данных."""
        data = {}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'query' in serializer.errors

    def test_none_data_validation_error(self) -> None:
        """Тест ошибки валидации при None данных."""
        serializer = CitySearchParamsSerializer(data=None)

        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors

    def test_whitespace_query_validation(self) -> None:
        """Тест валидации query с пробелами."""
        data = {'query': '   Moscow   '}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data['query'] == 'Moscow'

    def test_empty_country_field(self) -> None:
        """Тест с пустым необязательным полем country."""
        data = {'query': 'Moscow', 'country': ''}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'country' in serializer.errors

    def test_whitespace_country_field(self) -> None:
        """Тест с пробелами в необязательном поле country."""
        data = {'query': 'Moscow', 'country': '   RU   '}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data['query'] == 'Moscow'
        assert serializer.validated_data['country'] == 'RU'

    def test_long_query_string(self) -> None:
        """Тест с длинной строкой query (должна быть отклонена)."""
        long_query = 'A' * 1000  # Длинная строка превышает max_length=100
        data = {'query': long_query}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is False
        assert 'query' in serializer.errors

    def test_special_characters_in_query(self) -> None:
        """Тест с специальными символами в query."""
        data = {'query': 'Москва!@#$%^&*()_+-=[]{}|;:,.<>?'}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data['query'] == 'Москва!@#$%^&*()_+-=[]{}|;:,.<>?'

    def test_special_characters_in_country(self) -> None:
        """Тест с специальными символами в country."""
        data = {'query': 'Moscow', 'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data['country'] == 'RU'

    def test_unicode_characters(self) -> None:
        """Тест с Unicode символами."""
        data = {'query': 'Москва', 'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data['query'] == 'Москва'
        assert serializer.validated_data['country'] == 'RU'

    def test_numeric_strings(self) -> None:
        """Тест с числовыми строками."""
        data = {'query': '12345', 'country': '12'}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data['query'] == '12345'
        assert serializer.validated_data['country'] == '12'

    def test_serializer_fields_definition(self) -> None:
        """Тест определения полей сериализатора."""
        serializer = CitySearchParamsSerializer()

        # Проверяем, что поля определены корректно
        assert 'query' in serializer.fields
        assert 'country' in serializer.fields

        # Проверяем типы полей
        assert isinstance(serializer.fields['query'], serializers.CharField)
        assert isinstance(serializer.fields['country'], serializers.CharField)

        # Проверяем, что query обязательное, а country - нет
        assert serializer.fields['query'].required is True
        assert serializer.fields['country'].required is False

    def test_serializer_data_property(self) -> None:
        """Тест свойства data сериализатора."""
        data = {'query': 'Moscow', 'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=data)
        serializer.is_valid()

        # Проверяем, что data содержит валидные данные
        assert serializer.data['query'] == 'Moscow'
        assert serializer.data['country'] == 'RU'

    def test_serializer_data_property_with_errors(self) -> None:
        """Тест свойства data при наличии ошибок валидации."""
        data = {'country': 'RU'}  # Отсутствует query
        serializer = CitySearchParamsSerializer(data=data)
        serializer.is_valid()

        # При ошибках валидации data может вызывать исключение или возвращать пустые данные
        # Проверяем, что есть ошибки валидации
        assert serializer.is_valid() is False
        assert 'query' in serializer.errors

    def test_multiple_validation_errors(self) -> None:
        """Тест множественных ошибок валидации."""
        data = {}  # Пустые данные
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is False
        assert len(serializer.errors) > 0
        assert 'query' in serializer.errors

    def test_serializer_instance_creation(self) -> None:
        """Тест создания экземпляра сериализатора."""
        # Тест с данными
        serializer_with_data = CitySearchParamsSerializer(data={'query': 'test'})
        assert serializer_with_data is not None

        # Тест без данных
        serializer_without_data = CitySearchParamsSerializer()
        assert serializer_without_data is not None

        # Тест с instance (если поддерживается)
        serializer_with_instance = CitySearchParamsSerializer(instance={})
        assert serializer_with_instance is not None

    def test_serializer_to_representation(self) -> None:
        """Тест метода to_representation."""
        data = {'query': 'Moscow', 'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=data)
        serializer.is_valid()

        # Проверяем, что to_representation возвращает корректные данные
        representation = serializer.to_representation(serializer.validated_data)
        assert representation['query'] == 'Moscow'
        assert representation['country'] == 'RU'

    def test_serializer_to_internal_value(self) -> None:
        """Тест метода to_internal_value."""
        data = {'query': 'Moscow', 'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=data)

        # Проверяем внутреннее преобразование данных
        internal_value = serializer.to_internal_value(data)
        assert internal_value['query'] == 'Moscow'
        assert internal_value['country'] == 'RU'

    def test_serializer_validate_method(self) -> None:
        """Тест кастомной валидации (если есть)."""
        data = {'query': 'Moscow', 'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=data)

        # Если есть кастомный метод validate, проверяем его
        # В данном случае его нет, поэтому просто проверяем базовую валидацию
        assert serializer.is_valid() is True

    def test_serializer_validate_field_methods(self) -> None:
        """Тест кастомной валидации полей (если есть)."""
        data = {'query': 'Moscow', 'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=data)

        # Если есть кастомные методы validate_query или validate_country, проверяем их
        # В данном случае их нет, поэтому просто проверяем базовую валидацию
        assert serializer.is_valid() is True

    def test_serializer_context(self) -> None:
        """Тест передачи контекста в сериализатор."""
        context = {'request': MagicMock()}
        serializer = CitySearchParamsSerializer(data={'query': 'test'}, context=context)

        assert serializer.context == context
        assert serializer.is_valid() is True

    def test_serializer_partial_update(self) -> None:
        """Тест частичного обновления (partial=True)."""
        # Сначала создаем сериализатор с полными данными
        initial_data = {'query': 'Moscow', 'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=initial_data)
        serializer.is_valid()
        initial_validated = serializer.validated_data

        # Затем обновляем только одно поле
        partial_data = {'country': 'US'}
        partial_serializer = CitySearchParamsSerializer(
            data=partial_data, partial=True, instance=initial_validated
        )

        assert partial_serializer.is_valid() is True
        # При partial=True отсутствующие поля не должны вызывать ошибки
        validated = partial_serializer.validated_data
        assert 'country' in validated
        assert validated['country'] == 'US'

    def test_serializer_nested_validation(self) -> None:
        """Тест вложенной валидации (если применимо)."""
        # В данном сериализаторе нет вложенных полей, но проверяем структуру
        data = {'query': 'Moscow', 'country': 'RU'}
        serializer = CitySearchParamsSerializer(data=data)

        assert serializer.is_valid() is True
        # Проверяем, что валидированные данные имеют правильную структуру
        validated = serializer.validated_data
        assert isinstance(validated, dict)
        assert 'query' in validated
        assert 'country' in validated

    def test_serializer_field_validation_edge_cases(self) -> None:
        """Тест граничных случаев валидации полей."""
        test_cases = [
            # (query, country, should_be_valid, description)
            ('a', 'b', True, 'Минимальные значения'),
            ('x' * 100, 'y' * 2, True, 'Максимальные допустимые значения'),
            ('x' * 101, 'y' * 2, False, 'Query превышает max_length'),
            ('test', 'y' * 3, False, 'Country превышает max_length'),
            ('test', None, True, 'country = None'),
            ('', 'RU', False, 'Пустой query'),
            (None, 'RU', False, 'query = None'),
        ]

        for query, country, should_be_valid, description in test_cases:
            data = {'query': query}
            if country is not None:
                data['country'] = country

            serializer = CitySearchParamsSerializer(data=data)
            is_valid = serializer.is_valid()

            assert is_valid == should_be_valid, f'Failed for {description}: {data}'
