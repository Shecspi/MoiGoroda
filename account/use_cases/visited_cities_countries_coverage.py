# ----------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""
Сценарий подготовки статистики покрытия стран посещёнными городами.

HTTP-контроллер передаёт сюда уже проверенный user_id, а use case оркестрирует
репозитории и собирает API-схему ответа без прямой работы с ORM.
"""

from account.repository import get_total_users_count
from account.schemas import (
    PersonalVisitedCitiesCountriesCoverageResponse,
    VisitedCitiesCountryCoverage,
)
from country.repository import (
    get_countries_visited_city_counts,
    get_unique_visited_cities_country_ranks,
)
from services.cache import delete_cache, get_or_set_cache

# Rank и total_users_count допускают задержку актуализации до TTL:
# эти данные являются приблизительной статистикой, а не строгим leaderboard.
CACHE_TTL_SECONDS = 60 * 60
CACHE_KEY_TEMPLATE = 'account:stats:visited-cities:countries-coverage:v1:user:{user_id}'


type CachedCountryCoverage = dict[str, int | str]


def _get_cache_key(user_id: int) -> str:
    return CACHE_KEY_TEMPLATE.format(user_id=user_id)


def _build_response(
    countries_coverage: list[CachedCountryCoverage],
) -> PersonalVisitedCitiesCountriesCoverageResponse:
    return PersonalVisitedCitiesCountriesCoverageResponse(
        countries_coverage=[
            VisitedCitiesCountryCoverage(
                name=str(item['name']),
                visited_cities=int(item['visited_cities']),
                total_cities=int(item['total_cities']),
                rank=int(item['rank']),
                total_users_count=int(item['total_users_count']),
            )
            for item in countries_coverage
        ]
    )


def invalidate_personal_visited_cities_countries_coverage_cache(user_id: int) -> None:
    """Удаляет кеш статистики покрытия стран посещёнными городами для пользователя."""
    delete_cache(_get_cache_key(user_id))


def _build_countries_coverage(user_id: int) -> list[CachedCountryCoverage]:
    countries = get_countries_visited_city_counts(user_id)
    total_users_count = get_total_users_count()
    country_visit_counts = {country.pk: country.visited_cities for country in countries}
    country_ranks = get_unique_visited_cities_country_ranks(country_visit_counts)

    return [
        {
            'name': country.name,
            'visited_cities': country.visited_cities,
            'total_cities': country.total_cities,
            'rank': country_ranks[country.pk],
            'total_users_count': total_users_count,
        }
        for country in countries
    ]


def get_personal_visited_cities_countries_coverage(
    user_id: int,
) -> PersonalVisitedCitiesCountriesCoverageResponse:
    """
    Возвращает данные для блока «Посещённые города по странам» в статистике аккаунта.

    Страны отсортированы по количеству посещённых городов,
    для каждой страны указан rank пользователя среди всех пользователей.
    """
    countries_coverage = get_or_set_cache(
        key=_get_cache_key(user_id),
        ttl_seconds=CACHE_TTL_SECONDS,
        factory=lambda: _build_countries_coverage(user_id),
    )

    return _build_response(countries_coverage)
