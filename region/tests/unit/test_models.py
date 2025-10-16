"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

import pytest
from django.db import IntegrityError

from region.models import Area, RegionType, Region, TYPES_OF_REGIONS


@pytest.mark.unit
@pytest.mark.django_db
class TestAreaModel:
    """Тесты для модели Area"""

    def test_area_str_representation(self, test_area: Area) -> None:
        """Тест строкового представления области"""
        assert str(test_area) == 'Центральный федеральный округ'

    def test_area_title_unique(self, test_country: Any) -> None:
        """Тест уникальности названия области"""
        Area.objects.create(title='Test Area', country=test_country)

        with pytest.raises(IntegrityError):
            Area.objects.create(title='Test Area', country=test_country)

    def test_area_cascade_delete(self, test_area: Area, test_region: Region) -> None:
        """Тест каскадного удаления при удалении области"""
        area_id = test_area.id
        region_id = test_region.id

        test_area.delete()

        assert not Area.objects.filter(id=area_id).exists()
        # Region тоже удаляется (CASCADE)
        assert not Region.objects.filter(id=region_id).exists()

    def test_area_meta_verbose_name(self) -> None:
        """Тест verbose_name модели"""
        assert Area._meta.verbose_name == 'Федеральный округ'
        assert Area._meta.verbose_name_plural == 'Федеральные округа'


@pytest.mark.unit
@pytest.mark.django_db
class TestRegionTypeModel:
    """Тесты для модели RegionType"""

    def test_region_type_str_representation(self, test_region_type: RegionType) -> None:
        """Тест строкового представления типа региона"""
        assert str(test_region_type) == 'Область'

    def test_region_type_ordering(self) -> None:
        """Тест сортировки типов регионов"""
        RegionType.objects.create(title='Край')
        RegionType.objects.create(title='Республика')
        RegionType.objects.create(title='Автономный округ')

        types = list(RegionType.objects.all().order_by('title'))
        # Проверяем что первый элемент начинается с А
        assert types[0].title.startswith('А')
        # И последний с большей буквой
        assert types[-1].title > types[0].title

    def test_region_type_meta_verbose_name(self) -> None:
        """Тест verbose_name модели"""
        assert RegionType._meta.verbose_name == 'Тип региона'
        assert RegionType._meta.verbose_name_plural == 'Типы регионов'


@pytest.mark.unit
@pytest.mark.django_db
class TestRegionModel:
    """Тесты для модели Region"""

    def test_region_str_representation(self, test_region: Region) -> None:
        """Тест строкового представления региона"""
        assert str(test_region) == 'Московская область'

    def test_region_get_absolute_url(self, test_region: Region) -> None:
        """Тест получения абсолютного URL региона"""
        url = test_region.get_absolute_url()
        assert url == f'/region/{test_region.pk}/list'

    def test_region_unique_together(self, test_country: Any, test_region_type: RegionType) -> None:
        """Тест уникальности пары (title, type)"""
        Region.objects.create(
            title='Тестовый',
            full_name='Тестовый регион',
            country=test_country,
            type=test_region_type,
            iso3166='RU-TEST1',
        )

        # Попытка создать регион с таким же title и type должна вызвать ошибку
        with pytest.raises(IntegrityError):
            Region.objects.create(
                title='Тестовый',
                full_name='Другое полное название',
                country=test_country,
                type=test_region_type,
                iso3166='RU-TEST2',
            )

    def test_region_iso3166_unique(self, test_country: Any, test_region_type: RegionType) -> None:
        """Тест уникальности ISO3166 кода"""
        Region.objects.create(
            title='Первый',
            full_name='Первый регион',
            country=test_country,
            type=test_region_type,
            iso3166='RU-SAME',
        )

        with pytest.raises(IntegrityError):
            Region.objects.create(
                title='Второй',
                full_name='Второй регион',
                country=test_country,
                type=test_region_type,
                iso3166='RU-SAME',
            )

    def test_region_ordering(self, test_country: Any, test_region_type: RegionType) -> None:
        """Тест сортировки регионов по названию"""
        Region.objects.create(
            title='Б', full_name='Б', country=test_country, type=test_region_type, iso3166='RU-B'
        )
        Region.objects.create(
            title='А', full_name='А', country=test_country, type=test_region_type, iso3166='RU-A'
        )
        Region.objects.create(
            title='В', full_name='В', country=test_country, type=test_region_type, iso3166='RU-V'
        )

        regions = list(Region.objects.filter(country=test_country, type=test_region_type))
        assert regions[0].title == 'А'
        assert regions[1].title == 'Б'
        assert regions[2].title == 'В'

    def test_region_meta_verbose_name(self) -> None:
        """Тест verbose_name модели"""
        assert Region._meta.verbose_name == 'Регион'
        assert Region._meta.verbose_name_plural == 'Регионы'

    def test_region_can_have_null_area(
        self, test_country: Any, test_region_type: RegionType
    ) -> None:
        """Тест что area может быть None"""
        region = Region.objects.create(
            title='Без округа',
            full_name='Регион без округа',
            country=test_country,
            type=test_region_type,
            iso3166='RU-NO-AREA',
            area=None,
        )
        assert region.area is None


@pytest.mark.unit
class TestTypesOfRegionsConstant:
    """Тесты для константы TYPES_OF_REGIONS"""

    def test_types_of_regions_structure(self) -> None:
        """Тест структуры TYPES_OF_REGIONS"""
        assert isinstance(TYPES_OF_REGIONS, list)
        assert len(TYPES_OF_REGIONS) == 6

        for item in TYPES_OF_REGIONS:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)
            assert isinstance(item[1], str)

    def test_types_of_regions_contains_expected_types(self) -> None:
        """Тест что TYPES_OF_REGIONS содержит ожидаемые типы"""
        codes = [item[0] for item in TYPES_OF_REGIONS]
        names = [item[1] for item in TYPES_OF_REGIONS]

        assert 'R' in codes
        assert 'K' in codes
        assert 'O' in codes
        assert 'G' in codes
        assert 'AOb' in codes
        assert 'AOk' in codes

        assert 'республика' in names
        assert 'край' in names
        assert 'область' in names
        assert 'город федерального значения' in names
        assert 'автономная область' in names
        assert 'автономный округ' in names
