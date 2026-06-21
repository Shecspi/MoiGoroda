# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from typing import Any

import pytest
from django.core.cache import cache

from account.use_cases import visited_cities_countries_coverage as use_case
from country.dto import CountryVisitedCityCounts


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    cache.clear()


@pytest.mark.unit
def test_get_personal_visited_cities_countries_coverage_uses_cache(mocker: Any) -> None:
    countries_repo = mocker.patch.object(
        use_case,
        'get_countries_visited_city_counts',
        return_value=[
            CountryVisitedCityCounts(
                pk=1,
                name='Россия',
                visited_cities=10,
                total_cities=100,
            )
        ],
    )
    users_count_repo = mocker.patch.object(use_case, 'get_total_users_count', return_value=50)
    ranks_repo = mocker.patch.object(
        use_case,
        'get_unique_visited_cities_country_ranks',
        return_value={1: 3},
    )

    first_response = use_case.get_personal_visited_cities_countries_coverage(user_id=10)
    second_response = use_case.get_personal_visited_cities_countries_coverage(user_id=10)

    assert first_response == second_response
    assert countries_repo.call_count == 1
    assert users_count_repo.call_count == 1
    assert ranks_repo.call_count == 1
    assert first_response.countries_coverage[0].name == 'Россия'
    assert first_response.countries_coverage[0].rank == 3


@pytest.mark.unit
def test_invalidate_personal_visited_cities_countries_coverage_cache(mocker: Any) -> None:
    mocker.patch.object(use_case, 'get_countries_visited_city_counts', return_value=[])
    mocker.patch.object(use_case, 'get_total_users_count', return_value=0)
    mocker.patch.object(use_case, 'get_unique_visited_cities_country_ranks', return_value={})

    use_case.get_personal_visited_cities_countries_coverage(user_id=10)
    assert cache.get(use_case.CACHE_KEY_TEMPLATE.format(user_id=10)) == []

    use_case.invalidate_personal_visited_cities_countries_coverage_cache(user_id=10)

    assert cache.get(use_case.CACHE_KEY_TEMPLATE.format(user_id=10)) is None
