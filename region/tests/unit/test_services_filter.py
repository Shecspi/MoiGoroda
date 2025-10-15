"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime
from typing import Any

import pytest
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from region.services.filter import (
    apply_filter_to_queryset,
    filter_has_magnet,
    filter_has_no_magnet,
    filter_visited,
    filter_not_visited,
    filter_current_year,
    filter_last_year,
    FILTER_FUNCTIONS,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestFilterHasMagnet:
    """Тесты для фильтра has_magnet"""

    def test_filters_only_visited_cities_with_magnet(
        self,
        test_user: User,
        test_country: Any,
        test_region: Any,
    ) -> None:
        """Тест фильтрации только посещённых городов с сувениром"""
        city1 = City.objects.create(
            title='City1',
            region=test_region,
            country=test_country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )
        city2 = City.objects.create(
            title='City2',
            region=test_region,
            country=test_country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )

        # Посещаем оба города, но сувенир только из первого
        VisitedCity.objects.create(user=test_user, city=city1, has_magnet=True, rating=5)
        VisitedCity.objects.create(user=test_user, city=city2, has_magnet=False, rating=5)

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        filtered = filter_has_magnet(queryset, test_user)

        assert filtered.count() == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestFilterHasNoMagnet:
    """Тесты для фильтра has_no_magnet"""

    def test_filters_only_visited_cities_without_magnet(
        self,
        test_user: User,
        test_country: Any,
        test_region: Any,
    ) -> None:
        """Тест фильтрации только посещённых городов без сувенира"""
        city1 = City.objects.create(
            title='City1',
            region=test_region,
            country=test_country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )
        city2 = City.objects.create(
            title='City2',
            region=test_region,
            country=test_country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )

        VisitedCity.objects.create(user=test_user, city=city1, has_magnet=True, rating=5)
        VisitedCity.objects.create(user=test_user, city=city2, has_magnet=False, rating=5)

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        filtered = filter_has_no_magnet(queryset, test_user)

        assert filtered.count() == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestFilterVisited:
    """Тесты для фильтра visited"""

    def test_filters_only_visited_cities(
        self, test_user: User, test_country: Any, test_region: Any, test_city: City
    ) -> None:
        """Тест фильтрации только посещённых городов"""
        _ = City.objects.create(
            title='City2',
            region=test_region,
            country=test_country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )

        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        filtered = filter_visited(queryset, test_user)

        assert filtered.count() == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestFilterNotVisited:
    """Тесты для фильтра not_visited"""

    def test_filters_only_not_visited_cities(
        self, test_user: User, test_country: Any, test_region: Any, test_city: City
    ) -> None:
        """Тест фильтрации только непосещённых городов"""
        _ = City.objects.create(
            title='City2',
            region=test_region,
            country=test_country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )

        VisitedCity.objects.create(user=test_user, city=test_city, rating=5)

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        filtered = filter_not_visited(queryset, test_user)

        assert filtered.count() == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestFilterCurrentYear:
    """Тесты для фильтра current_year"""

    def test_filters_cities_visited_in_current_year(
        self, test_user: User, test_country: Any, test_region: Any
    ) -> None:
        """Тест фильтрации городов, посещённых в текущем году"""
        city1 = City.objects.create(
            title='City1',
            region=test_region,
            country=test_country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )
        city2 = City.objects.create(
            title='City2',
            region=test_region,
            country=test_country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )

        current_year = datetime.now().year
        last_year = current_year - 1

        VisitedCity.objects.create(
            user=test_user, city=city1, date_of_visit=datetime(current_year, 1, 1).date(), rating=5
        )
        VisitedCity.objects.create(
            user=test_user, city=city2, date_of_visit=datetime(last_year, 1, 1).date(), rating=5
        )

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        filtered = filter_current_year(queryset, test_user)

        assert filtered.count() == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestFilterLastYear:
    """Тесты для фильтра last_year"""

    def test_filters_cities_visited_in_last_year(
        self, test_user: User, test_country: Any, test_region: Any
    ) -> None:
        """Тест фильтрации городов, посещённых в прошлом году"""
        city1 = City.objects.create(
            title='City1',
            region=test_region,
            country=test_country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )
        city2 = City.objects.create(
            title='City2',
            region=test_region,
            country=test_country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )

        current_year = datetime.now().year
        last_year = current_year - 1

        VisitedCity.objects.create(
            user=test_user, city=city1, date_of_visit=datetime(current_year, 1, 1).date(), rating=5
        )
        VisitedCity.objects.create(
            user=test_user, city=city2, date_of_visit=datetime(last_year, 1, 1).date(), rating=5
        )

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        filtered = filter_last_year(queryset, test_user)

        assert filtered.count() == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestApplyFilterToQueryset:
    """Тесты для функции apply_filter_to_queryset"""

    def test_raises_key_error_for_unknown_filter(
        self, test_user: User, test_region: Any
    ) -> None:
        """Тест что выбрасывается KeyError для неизвестного фильтра"""
        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)

        with pytest.raises(KeyError, match='Неизвестный фильтр'):
            apply_filter_to_queryset(queryset, test_user, 'unknown_filter')

    def test_applies_magnet_filter(
        self, test_user: User, test_country: Any, test_region: Any, test_city: City
    ) -> None:
        """Тест применения фильтра magnet"""
        VisitedCity.objects.create(user=test_user, city=test_city, has_magnet=True, rating=5)

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        filtered = apply_filter_to_queryset(queryset, test_user, 'magnet')

        assert filtered.count() >= 1


@pytest.mark.unit
class TestFilterFunctionsDict:
    """Тесты для словаря FILTER_FUNCTIONS"""

    def test_filter_functions_contains_all_filters(self) -> None:
        """Тест что FILTER_FUNCTIONS содержит все фильтры"""
        expected_filters = {
            'magnet',
            'no_magnet',
            'current_year',
            'last_year',
            'visited',
            'not_visited',
        }
        assert set(FILTER_FUNCTIONS.keys()) == expected_filters

    def test_all_filter_functions_are_callable(self) -> None:
        """Тест что все значения в FILTER_FUNCTIONS являются callable"""
        for func in FILTER_FUNCTIONS.values():
            assert callable(func)

