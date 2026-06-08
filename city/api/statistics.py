from __future__ import annotations

from http import HTTPStatus

from django.http import Http404
from prometheus_client import Counter
from dmr import Controller, ResponseSpec, modify
from dmr.plugins.msgspec import MsgspecSerializer

from city.models import City
from city.repository.city_repository import CityRepository
from city.schemas import CityStatisticsResponse, NeighboringCityItem

city_statistics_loaded_total = Counter(
    'city_statistics_loaded_total',
    'Number of successful city statistics API responses',
)


class CityStatisticsController(Controller[MsgspecSerializer]):
    """
    API endpoint для загрузки статистики города.
    Вызывается через AJAX при открытии модального окна со статистикой.
    """

    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(dict[str, str], status_code=HTTPStatus.NOT_FOUND),
        ],
        tags=['Статистика городов'],
    )
    def get(self) -> CityStatisticsResponse:
        city_id = int(self.kwargs['city_id'])
        c_repo = CityRepository()

        try:
            city = c_repo.get_by_id(city_id)
        except City.DoesNotExist:
            raise Http404

        city_statistics_loaded_total.inc()

        number_of_cities_in_country = c_repo.get_number_of_cities(city.country.code)
        number_of_cities_in_region = c_repo.get_number_of_cities_in_region_by_city(city_id)

        # Ранги
        rank_in_country_by_visits = c_repo.get_rank_in_country_by_visits(city_id)
        rank_in_country_by_users = c_repo.get_rank_in_country_by_users(city_id)
        rank_in_region_by_visits = c_repo.get_rank_in_region_by_visits(city_id)
        rank_in_region_by_users = c_repo.get_rank_in_region_by_users(city_id)

        # Соседние города
        neighboring_cities_by_rank_in_region_by_users = (
            c_repo.get_neighboring_cities_by_rank_in_region_by_users(city_id)
        )
        neighboring_cities_by_rank_in_region_by_visits = (
            c_repo.get_neighboring_cities_by_rank_in_region_by_visits(city_id)
        )
        neighboring_cities_by_rank_in_country_by_users = (
            c_repo.get_neighboring_cities_by_rank_in_country_by_users(city_id)
        )
        neighboring_cities_by_rank_in_country_by_visits = (
            c_repo.get_neighboring_cities_by_rank_in_country_by_visits(city_id)
        )

        return CityStatisticsResponse(
            number_of_cities_in_country=number_of_cities_in_country,
            number_of_cities_in_region=number_of_cities_in_region,
            rank_in_country_by_visits=rank_in_country_by_visits,
            rank_in_country_by_users=rank_in_country_by_users,
            rank_in_region_by_visits=rank_in_region_by_visits,
            rank_in_region_by_users=rank_in_region_by_users,
            neighboring_cities_by_rank_in_country_by_users=[
                NeighboringCityItem(**c) for c in neighboring_cities_by_rank_in_country_by_users
            ],
            neighboring_cities_by_rank_in_country_by_visits=[
                NeighboringCityItem(**c) for c in neighboring_cities_by_rank_in_country_by_visits
            ],
            neighboring_cities_by_rank_in_region_by_users=[
                NeighboringCityItem(**c) for c in neighboring_cities_by_rank_in_region_by_users
            ],
            neighboring_cities_by_rank_in_region_by_visits=[
                NeighboringCityItem(**c) for c in neighboring_cities_by_rank_in_region_by_visits
            ],
        )
