"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

import pytest
from rest_framework import serializers

from region.models import Region
from region.serializers import RegionSerializer, RegionSearchParamsSerializer


@pytest.mark.unit
class TestRegionSerializer:
    """Тесты для RegionSerializer"""

    def test_serializer_has_required_fields(self) -> None:
        """Тест что сериализатор содержит необходимые поля"""
        serializer = RegionSerializer()
        assert 'id' in serializer.fields
        assert 'title' in serializer.fields

    def test_serializer_field_types(self) -> None:
        """Тест типов полей сериализатора"""
        serializer = RegionSerializer()
        assert isinstance(serializer.fields['id'], serializers.IntegerField)
        assert isinstance(serializer.fields['title'], serializers.SerializerMethodField)

    def test_serializer_meta_model(self) -> None:
        """Тест что используется правильная модель"""
        assert RegionSerializer.Meta.model == Region

    def test_serializer_meta_fields(self) -> None:
        """Тест что указаны правильные поля в Meta"""
        assert RegionSerializer.Meta.fields == ['id', 'title']

    @pytest.mark.django_db
    def test_get_title_returns_full_name(
        self, test_country: Any, test_region_type: Any, test_area: Any
    ) -> None:
        """Тест что get_title возвращает полное название региона"""
        region = Region.objects.create(
            title='Московская',
            full_name='Московская область',
            country=test_country,
            type=test_region_type,
            area=test_area,
            iso3166='RU-MOS',
        )

        serializer = RegionSerializer(region)
        assert serializer.data['title'] == 'Московская область'

    @pytest.mark.django_db
    def test_serializer_serializes_region(
        self, test_country: Any, test_region_type: Any, test_area: Any
    ) -> None:
        """Тест сериализации региона"""
        region = Region.objects.create(
            title='Московская',
            full_name='Московская область',
            country=test_country,
            type=test_region_type,
            area=test_area,
            iso3166='RU-MOS',
        )

        serializer = RegionSerializer(region)
        data = serializer.data

        assert data['id'] == region.id
        assert data['title'] == 'Московская область'

    @pytest.mark.django_db
    def test_serializer_serializes_list_of_regions(
        self, test_country: Any, test_region_type: Any, test_area: Any
    ) -> None:
        """Тест сериализации списка регионов"""
        regions = [
            Region.objects.create(
                title=f'Region{i}',
                full_name=f'Full Region {i}',
                country=test_country,
                type=test_region_type,
                area=test_area,
                iso3166=f'RU-R{i}',
            )
            for i in range(3)
        ]

        serializer = RegionSerializer(regions, many=True)
        data = serializer.data

        assert len(data) == 3
        assert data[0]['title'] == 'Full Region 0'
        assert data[1]['title'] == 'Full Region 1'
        assert data[2]['title'] == 'Full Region 2'


@pytest.mark.unit
class TestRegionSearchParamsSerializer:
    """Тесты для RegionSearchParamsSerializer"""

    def test_serializer_has_required_fields(self) -> None:
        """Тест что сериализатор содержит необходимые поля"""
        serializer = RegionSearchParamsSerializer()
        assert 'query' in serializer.fields
        assert 'country' in serializer.fields

    def test_serializer_field_types(self) -> None:
        """Тест типов полей сериализатора"""
        serializer = RegionSearchParamsSerializer()
        assert isinstance(serializer.fields['query'], serializers.CharField)
        assert isinstance(serializer.fields['country'], serializers.CharField)

    def test_query_field_is_required(self) -> None:
        """Тест что поле query обязательное"""
        serializer = RegionSearchParamsSerializer()
        assert serializer.fields['query'].required is True

    def test_country_field_is_optional(self) -> None:
        """Тест что поле country необязательное"""
        serializer = RegionSearchParamsSerializer()
        assert serializer.fields['country'].required is False

    def test_serializer_validates_valid_data(self) -> None:
        """Тест валидации корректных данных"""
        data = {'query': 'Москва', 'country': 'RU'}
        serializer = RegionSearchParamsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['query'] == 'Москва'
        assert serializer.validated_data['country'] == 'RU'

    def test_serializer_validates_data_without_country(self) -> None:
        """Тест валидации данных без поля country"""
        data = {'query': 'Москва'}
        serializer = RegionSearchParamsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['query'] == 'Москва'
        assert 'country' not in serializer.validated_data

    def test_serializer_fails_without_query(self) -> None:
        """Тест что валидация не проходит без обязательного поля query"""
        data = {'country': 'RU'}
        serializer = RegionSearchParamsSerializer(data=data)
        assert not serializer.is_valid()
        assert 'query' in serializer.errors

    def test_serializer_rejects_empty_country(self) -> None:
        """Тест что пустое значение country не принимается"""
        data = {'query': 'Москва', 'country': ''}
        serializer = RegionSearchParamsSerializer(data=data)
        assert not serializer.is_valid()
        assert 'country' in serializer.errors
