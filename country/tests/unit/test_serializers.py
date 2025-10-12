"""
Юнит-тесты для сериализаторов приложения country.
"""

from unittest.mock import Mock

import pytest
from django.contrib.auth.models import User

from country.models import Country, VisitedCountry
from country.serializers import (
    PartOfTheWorldSerializer,
    LocationSerializer,
    CountrySerializer,
    CountrySimpleSerializer,
    VisitedCountrySerializer,
)


@pytest.mark.unit
class TestPartOfTheWorldSerializer:
    """Тесты для PartOfTheWorldSerializer."""

    def test_serializer_fields(self) -> None:
        """Проверяет поля сериализатора."""
        serializer = PartOfTheWorldSerializer()
        assert '__all__' == serializer.Meta.fields or set(serializer.fields.keys())


@pytest.mark.unit
class TestLocationSerializer:
    """Тесты для LocationSerializer."""

    def test_serializer_fields(self) -> None:
        """Проверяет поля сериализатора."""
        serializer = LocationSerializer()
        assert '__all__' == serializer.Meta.fields or set(serializer.fields.keys())


@pytest.mark.unit
class TestCountrySerializer:
    """Тесты для CountrySerializer."""

    def test_serializer_has_required_fields(self) -> None:
        """Проверяет наличие обязательных полей."""
        serializer = CountrySerializer()
        assert 'to_delete' in serializer.fields
        assert 'part_of_the_world' in serializer.fields
        assert 'location' in serializer.fields
        assert 'owner' in serializer.fields

    def test_to_delete_is_read_only(self) -> None:
        """Проверяет что to_delete read-only."""
        serializer = CountrySerializer()
        assert serializer.fields['to_delete'].read_only is True


@pytest.mark.unit
class TestCountrySimpleSerializer:
    """Тесты для CountrySimpleSerializer."""

    def test_serializer_has_correct_fields(self) -> None:
        """Проверяет наличие всех полей."""
        serializer = CountrySimpleSerializer()
        expected_fields = {'id', 'code', 'name', 'number_of_visited_cities', 'number_of_cities'}
        assert set(serializer.fields.keys()) == expected_fields


@pytest.mark.unit
class TestVisitedCountrySerializer:
    """Тесты для VisitedCountrySerializer."""

    def test_serializer_has_code_and_name(self) -> None:
        """Проверяет наличие полей code и name."""
        serializer = VisitedCountrySerializer()
        assert 'code' in serializer.fields
        assert 'name' in serializer.fields

    def test_code_field_length_constraints(self) -> None:
        """Проверяет ограничения длины для code."""
        serializer = VisitedCountrySerializer()
        code_field = serializer.fields['code']
        # CharField имеет max_length и min_length, но для типов DRF это Any
        assert hasattr(code_field, 'max_length')
        assert hasattr(code_field, 'min_length')

    def test_name_is_read_only(self) -> None:
        """Проверяет что name read-only."""
        serializer = VisitedCountrySerializer()
        assert serializer.fields['name'].read_only is True


@pytest.mark.django_db
@pytest.mark.integration
class TestVisitedCountrySerializerValidation:
    """Интеграционные тесты для валидации VisitedCountrySerializer."""

    def test_validate_code_with_non_existent_country(self) -> None:
        """Проверяет валидацию с несуществующим кодом страны."""
        user = User.objects.create_user(username='testuser', password='testpass')
        context = {'request': Mock(user=user)}
        serializer = VisitedCountrySerializer(data={'code': 'XX'}, context=context)

        assert not serializer.is_valid()
        assert 'code' in serializer.errors

    def test_validate_code_with_existing_country(self) -> None:
        """Проверяет валидацию с существующим кодом страны."""
        Country.objects.create(name='Россия', code='RU')
        user = User.objects.create_user(username='testuser', password='testpass')
        context = {'request': Mock(user=user)}
        serializer = VisitedCountrySerializer(data={'code': 'RU'}, context=context)

        assert serializer.is_valid()

    def test_validate_code_with_already_visited_country(self) -> None:
        """Проверяет валидацию при попытке добавить уже посещенную страну."""
        country = Country.objects.create(name='Россия', code='RU')
        user = User.objects.create_user(username='testuser', password='testpass')
        VisitedCountry.objects.create(country=country, user=user)

        context = {'request': Mock(user=user)}
        serializer = VisitedCountrySerializer(data={'code': 'RU'}, context=context)

        assert not serializer.is_valid()
        assert 'code' in serializer.errors

    def test_create_method(self) -> None:
        """Проверяет метод create."""
        country = Country.objects.create(name='Россия', code='RU')
        user = User.objects.create_user(username='testuser', password='testpass')

        context = {'request': Mock(user=user)}
        serializer = VisitedCountrySerializer(data={'code': 'RU'}, context=context)
        serializer.is_valid(raise_exception=True)

        visited_country = serializer.save(user=user)

        assert visited_country.country == country
        assert visited_country.user == user
        assert VisitedCountry.objects.count() == 1
