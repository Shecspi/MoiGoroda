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


def get_personal_visited_cities_countries_coverage(
    user_id: int,
) -> PersonalVisitedCitiesCountriesCoverageResponse:
    """
    Возвращает данные для блока «Посещённые города по странам» в статистике аккаунта.

    Чтраны отсортированы по количеству посещённых городов,
    для каждой страны указан rank пользователя среди всех пользователей.
    """
    countries = get_countries_visited_city_counts(user_id)
    total_users_count = get_total_users_count()
    country_visit_counts = {country.pk: country.visited_cities for country in countries}
    country_ranks = get_unique_visited_cities_country_ranks(country_visit_counts)

    return PersonalVisitedCitiesCountriesCoverageResponse(
        countries_coverage=[
            VisitedCitiesCountryCoverage(
                name=country.name,
                visited_cities=country.visited_cities,
                total_cities=country.total_cities,
                rank=country_ranks[country.pk],
                total_users_count=total_users_count,
            )
            for country in countries
        ]
    )
