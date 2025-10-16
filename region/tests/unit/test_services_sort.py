"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""
# mypy: disable-error-code="misc"

from datetime import datetime
from typing import Any

import pytest
from django.contrib.auth.models import User

from city.models import City, VisitedCity
from region.services.sort import (
    apply_sort_to_queryset,
    sort_by_name_up,
    sort_by_name_down,
    sort_by_first_visit_date_down,
    sort_by_last_visit_date_up,
    SORT_FUNCTIONS,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestSortByName:
    """Тесты для сортировки по названию"""

    def test_sort_by_name_up(self, test_user: User, test_country: Any, test_region: Any) -> None:
        """Тест сортировки по названию от А до Я"""
        city_a = City.objects.create(
            title='А-город',
            region=test_region,
            country=test_country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )
        city_z = City.objects.create(
            title='Я-город',
            region=test_region,
            country=test_country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )

        VisitedCity.objects.create(user=test_user, city=city_a, rating=5)
        VisitedCity.objects.create(user=test_user, city=city_z, rating=5)

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        sorted_qs = sort_by_name_up(queryset)

        cities = list(sorted_qs.values_list('title', flat=True))
        assert cities[0] == 'А-город'

    def test_sort_by_name_down(self, test_user: User, test_country: Any, test_region: Any) -> None:
        """Тест сортировки по названию от Я до А"""
        city_a = City.objects.create(
            title='А-город',
            region=test_region,
            country=test_country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )
        city_z = City.objects.create(
            title='Я-город',
            region=test_region,
            country=test_country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )

        VisitedCity.objects.create(user=test_user, city=city_a, rating=5)
        VisitedCity.objects.create(user=test_user, city=city_z, rating=5)

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        sorted_qs = sort_by_name_down(queryset)

        cities = list(sorted_qs.values_list('title', flat=True))
        assert cities[0] == 'Я-город'


@pytest.mark.unit
@pytest.mark.django_db
class TestSortByVisitDate:
    """Тесты для сортировки по датам посещения"""

    def test_sort_by_first_visit_date_down(
        self, test_user: User, test_country: Any, test_region: Any
    ) -> None:
        """Тест сортировки по первой дате посещения (новые первыми)"""
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

        VisitedCity.objects.create(
            user=test_user, city=city1, date_of_visit=datetime(2024, 1, 1).date(), rating=5
        )
        VisitedCity.objects.create(
            user=test_user, city=city2, date_of_visit=datetime(2024, 12, 31).date(), rating=5
        )

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        sorted_qs = sort_by_first_visit_date_down(queryset)

        # Город с более поздней датой должен быть первым
        cities_with_dates = list(
            sorted_qs.filter(first_visit_date__isnull=False).values('title', 'first_visit_date')
        )
        if len(cities_with_dates) >= 2:
            assert (
                cities_with_dates[0]['first_visit_date'] >= cities_with_dates[1]['first_visit_date']
            )

    def test_sort_by_last_visit_date_up(
        self, test_user: User, test_country: Any, test_region: Any
    ) -> None:
        """Тест сортировки по последней дате посещения (старые первыми)"""
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

        VisitedCity.objects.create(
            user=test_user, city=city1, date_of_visit=datetime(2024, 1, 1).date(), rating=5
        )
        VisitedCity.objects.create(
            user=test_user, city=city2, date_of_visit=datetime(2024, 12, 31).date(), rating=5
        )

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        sorted_qs = sort_by_last_visit_date_up(queryset)

        # Город с более ранней датой должен быть первым (среди городов с датами)
        cities_with_dates = list(
            sorted_qs.filter(last_visit_date__isnull=False).values('title', 'last_visit_date')
        )
        if len(cities_with_dates) >= 2:
            assert (
                cities_with_dates[0]['last_visit_date'] <= cities_with_dates[1]['last_visit_date']
            )


@pytest.mark.unit
@pytest.mark.django_db
class TestApplySortToQueryset:
    """Тесты для функции apply_sort_to_queryset"""

    def test_raises_key_error_for_unknown_sort(self, test_user: User, test_region: Any) -> None:
        """Тест что выбрасывается KeyError для неизвестной сортировки"""
        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)

        with pytest.raises(KeyError, match='Неизвестный параметр сортировки'):
            apply_sort_to_queryset(queryset, 'unknown_sort', is_authenticated=True)

    def test_applies_sort_for_authenticated_user(
        self, test_user: User, test_country: Any, test_region: Any
    ) -> None:
        """Тест применения сортировки для авторизованного пользователя"""
        city1 = City.objects.create(
            title='А-город',
            region=test_region,
            country=test_country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )
        _ = City.objects.create(
            title='Я-город',
            region=test_region,
            country=test_country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )

        VisitedCity.objects.create(user=test_user, city=city1, rating=5)

        from region.services.db import get_all_cities_in_region

        queryset = get_all_cities_in_region(test_user, test_region.id)
        sorted_qs = apply_sort_to_queryset(queryset, 'name_up', is_authenticated=True)

        cities = list(sorted_qs.values_list('title', flat=True))
        assert cities[0] == 'А-город'

    def test_applies_default_sort_for_unauthenticated_user(
        self, test_country: Any, test_region: Any
    ) -> None:
        """Тест применения сортировки по умолчанию для неавторизованного пользователя"""
        City.objects.create(
            title='Я-город',
            region=test_region,
            country=test_country,
            coordinate_width=55.0,
            coordinate_longitude=37.0,
        )
        City.objects.create(
            title='А-город',
            region=test_region,
            country=test_country,
            coordinate_width=56.0,
            coordinate_longitude=38.0,
        )

        queryset = City.objects.filter(region=test_region)
        sorted_qs = apply_sort_to_queryset(queryset, 'any', is_authenticated=False)

        cities = list(sorted_qs.values_list('title', flat=True))
        assert cities[0] == 'А-город'


@pytest.mark.unit
class TestSortFunctionsDict:
    """Тесты для словаря SORT_FUNCTIONS"""

    def test_sort_functions_contains_all_sorts(self) -> None:
        """Тест что SORT_FUNCTIONS содержит все сортировки"""
        expected_sorts = {
            'name_down',
            'name_up',
            'first_visit_date_down',
            'first_visit_date_up',
            'last_visit_date_down',
            'last_visit_date_up',
            'date_of_foundation_down',
            'date_of_foundation_up',
            'number_of_users_who_visit_city_down',
            'number_of_users_who_visit_city_up',
            'number_of_visits_all_users_down',
            'number_of_visits_all_users_up',
        }
        assert set(SORT_FUNCTIONS.keys()) == expected_sorts

    def test_all_sort_functions_are_callable(self) -> None:
        """Тест что все значения в SORT_FUNCTIONS являются callable"""
        for func in SORT_FUNCTIONS.values():
            assert callable(func)
