"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""
# mypy: disable-error-code="union-attr"

from typing import Any

import pytest
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from country.models import Country
from region.models import Region
from region.services.db import (
    get_all_regions,
    get_number_of_regions,
    get_all_region_with_visited_cities,
    get_number_of_visited_regions,
    get_number_of_finished_regions,
    get_visited_areas,
    get_number_all_areas,
    get_number_visited_areas,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestGetAllRegions:
    """Тесты для функции get_all_regions"""

    def test_returns_all_regions_without_country_filter(
        self, test_country: Any, test_region_type: Any, test_area: Any
    ) -> None:
        """Тест возврата всех регионов без фильтра по стране"""
        Region.objects.create(
            title='Region1',
            full_name='Region 1',
            country=test_country,
            type=test_region_type,
            iso3166='RU-R1',
        )
        Region.objects.create(
            title='Region2',
            full_name='Region 2',
            country=test_country,
            type=test_region_type,
            iso3166='RU-R2',
        )

        queryset = get_all_regions()
        assert queryset.count() >= 2

    def test_returns_regions_filtered_by_country(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест фильтрации регионов по стране"""
        other_country = Country.objects.create(name='США', code='US')

        Region.objects.create(
            title='Region1',
            full_name='Region 1',
            country=test_country,
            type=test_region_type,
            iso3166='RU-R1',
        )
        Region.objects.create(
            title='Region2',
            full_name='Region 2',
            country=other_country,
            type=test_region_type,
            iso3166='US-R1',
        )

        queryset = get_all_regions(country_id=test_country.id)
        assert queryset.count() == 1
        assert queryset.first().title == 'Region1'

    def test_annotates_num_total(
        self, test_country: Any, test_region_type: Any, test_region: Region, test_city: City
    ) -> None:
        """Тест что добавляется аннотация num_total"""
        queryset = get_all_regions(country_id=test_country.id)
        region_with_count = queryset.filter(id=test_region.id).first()

        assert hasattr(region_with_count, 'num_total')
        assert region_with_count.num_total >= 1

    def test_orders_by_title(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест сортировки по title"""
        Region.objects.create(
            title='Я',
            full_name='Я регион',
            country=test_country,
            type=test_region_type,
            iso3166='RU-YA',
        )
        Region.objects.create(
            title='А',
            full_name='А регион',
            country=test_country,
            type=test_region_type,
            iso3166='RU-A',
        )

        queryset = get_all_regions(country_id=test_country.id)
        regions = list(queryset)

        assert regions[0].title == 'А'
        assert regions[-1].title == 'Я'


@pytest.mark.unit
@pytest.mark.django_db
class TestGetNumberOfRegions:
    """Тесты для функции get_number_of_regions"""

    def test_returns_total_count_without_filter(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест подсчёта всех регионов без фильтра"""
        initial_count = get_number_of_regions(None)

        Region.objects.create(
            title='Test', full_name='Test', country=test_country, type=test_region_type, iso3166='RU-T1'
        )

        assert get_number_of_regions(None) == initial_count + 1

    def test_returns_count_filtered_by_country(
        self, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест подсчёта регионов с фильтром по стране"""
        other_country = Country.objects.create(name='США', code='US')

        Region.objects.create(
            title='RU Region',
            full_name='RU Region',
            country=test_country,
            type=test_region_type,
            iso3166='RU-R',
        )
        Region.objects.create(
            title='US Region',
            full_name='US Region',
            country=other_country,
            type=test_region_type,
            iso3166='US-R',
        )

        assert get_number_of_regions(test_country.id) == 1
        assert get_number_of_regions(other_country.id) == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestGetAllRegionWithVisitedCities:
    """Тесты для функции get_all_region_with_visited_cities"""

    def test_annotates_num_total_and_num_visited(
        self,
        test_user: User,
        test_country: Any,
        test_region: Region,
        test_city: City,
    ) -> None:
        """Тест что добавляются аннотации num_total и num_visited"""
        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        queryset = get_all_region_with_visited_cities(test_user.id, test_country.id)
        region = queryset.filter(id=test_region.id).first()

        assert hasattr(region, 'num_total')
        assert hasattr(region, 'num_visited')
        assert region.num_total >= 1
        assert region.num_visited >= 1

    def test_num_visited_zero_for_unvisited_cities(
        self, test_user: User, test_country: Any, test_region: Region, test_city: City
    ) -> None:
        """Тест что num_visited равен 0 для непосещённых городов"""
        queryset = get_all_region_with_visited_cities(test_user.id, test_country.id)
        region = queryset.filter(id=test_region.id).first()

        assert region.num_visited == 0

    def test_annotates_ratio_visited(
        self, test_user: User, test_country: Any, test_region: Region, test_city: City
    ) -> None:
        """Тест что добавляется аннотация ratio_visited"""
        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        queryset = get_all_region_with_visited_cities(test_user.id, test_country.id)
        region = queryset.filter(id=test_region.id).first()

        assert hasattr(region, 'ratio_visited')
        assert region.ratio_visited >= 0

    def test_filters_by_country(
        self, test_user: User, test_country: Any, test_region_type: Any
    ) -> None:
        """Тест фильтрации по стране"""
        other_country = Country.objects.create(name='США', code='US')
        Region.objects.create(
            title='US Region',
            full_name='US Region',
            country=other_country,
            type=test_region_type,
            iso3166='US-R',
        )

        queryset = get_all_region_with_visited_cities(test_user.id, test_country.id)
        assert all(region.country_id == test_country.id for region in queryset)


@pytest.mark.unit
@pytest.mark.django_db
class TestGetNumberOfVisitedRegions:
    """Тесты для функции get_number_of_visited_regions"""

    def test_returns_zero_when_no_visits(self, test_user: User, test_country: Any) -> None:
        """Тест что возвращает 0 когда нет посещений"""
        count = get_number_of_visited_regions(test_user.id, test_country.id)
        assert count == 0

    def test_returns_count_of_visited_regions(
        self,
        test_user: User,
        test_country: Any,
        test_region: Region,
        test_city: City,
    ) -> None:
        """Тест подсчёта посещённых регионов"""
        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        count = get_number_of_visited_regions(test_user.id, test_country.id)
        assert count >= 1

    def test_counts_only_regions_with_at_least_one_visit(
        self,
        test_user: User,
        test_country: Any,
        test_region_type: Any,
        test_region: Region,
        test_city: City,
    ) -> None:
        """Тест что считаются только регионы хотя бы с одним посещением"""
        # Создаём регион без посещений
        Region.objects.create(
            title='Empty',
            full_name='Empty Region',
            country=test_country,
            type=test_region_type,
            iso3166='RU-EMPTY',
        )

        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        count = get_number_of_visited_regions(test_user.id, test_country.id)
        # Должен быть 1, а не 2
        assert count == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestGetNumberOfFinishedRegions:
    """Тесты для функции get_number_of_finished_regions"""

    def test_returns_zero_when_no_finished_regions(
        self, test_user: User, test_country: Any
    ) -> None:
        """Тест что возвращает 0 когда нет завершённых регионов"""
        count = get_number_of_finished_regions(test_user.id, test_country.id)
        assert count == 0

    def test_counts_only_fully_visited_regions(
        self,
        test_user: User,
        test_country: Any,
        test_region: Region,
        test_city: City,
    ) -> None:
        """Тест что считаются только полностью посещённые регионы"""
        # Создаём второй город в том же регионе
        city2 = City.objects.create(
            title='City2',
            region=test_region,
            country=test_country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )

        # Посещаем только один город
        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        count = get_number_of_finished_regions(test_user.id, test_country.id)
        # Регион не должен считаться завершённым
        assert count == 0

        # Посещаем второй город
        VisitedCity.objects.create(user=test_user, city=city2, rating=5)

        count = get_number_of_finished_regions(test_user.id, test_country.id)
        # Теперь регион должен быть завершён
        assert count == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestGetVisitedAreas:
    """Тесты для функции get_visited_areas"""

    def test_returns_queryset_with_annotations(
        self,
        test_user: User,
        test_area: Any,
        test_region: Region,
        test_city: City,
    ) -> None:
        """Тест что возвращается QuerySet с аннотациями"""
        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        queryset = get_visited_areas(test_user.id)
        area = queryset.filter(id=test_area.id).first()

        assert hasattr(area, 'total_regions')
        assert hasattr(area, 'visited_regions')
        assert hasattr(area, 'ratio_visited')

    def test_calculates_ratio_correctly(
        self,
        test_user: User,
        test_country: Any,
        test_region_type: Any,
        test_area: Any,
        test_region: Region,
        test_city: City,
    ) -> None:
        """Тест правильности расчёта ratio_visited"""
        # Создаём второй регион в том же округе без посещений
        _ = Region.objects.create(
            title='Region2',
            full_name='Region 2',
            country=test_country,
            type=test_region_type,
            area=test_area,
            iso3166='RU-R2',
        )

        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        queryset = get_visited_areas(test_user.id)
        area = queryset.filter(id=test_area.id).first()

        # В округе 2 региона, посещён 1 - должно быть 50%
        assert area.total_regions == 2
        assert area.visited_regions == 1
        assert 49 <= area.ratio_visited <= 51  # С учётом округления


@pytest.mark.unit
@pytest.mark.django_db
class TestGetNumberAllAreas:
    """Тесты для функции get_number_all_areas"""

    def test_returns_total_count(self, test_area: Any) -> None:
        """Тест возврата общего количества округов"""
        initial_count = get_number_all_areas()
        assert initial_count >= 1


@pytest.mark.unit
@pytest.mark.django_db
class TestGetNumberVisitedAreas:
    """Тесты для функции get_number_visited_areas"""

    def test_returns_zero_when_no_visits(self, test_user: User) -> None:
        """Тест что возвращает 0 когда нет посещений"""
        count = get_number_visited_areas(test_user.id)
        assert count == 0

    def test_counts_areas_with_visits(
        self,
        test_user: User,
        test_area: Any,
        test_region: Region,
        test_city: City,
    ) -> None:
        """Тест подсчёта округов с посещениями"""
        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        count = get_number_visited_areas(test_user.id)
        assert count >= 1

