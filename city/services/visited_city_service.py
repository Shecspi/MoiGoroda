from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest, Http404

from city.dto import CityDetailsDTO
from city.models import City
from city.repository.interfaces import AbstractCityRepository, AbstractVisitedCityRepository
from city.services.db import (
    get_number_of_users_who_visit_city,
    get_total_number_of_visits,
    get_number_of_cities,
    get_number_of_cities_in_region_by_city,
    get_rank_by_visits_of_city,
    get_rank_by_users_of_city,
    get_rank_by_visits_of_city_in_region,
    get_rank_by_users_of_city_in_region,
    get_neighboring_cities_by_users_rank,
    get_neighboring_cities_by_visits_rank,
    get_neighboring_cities_in_region_by_users_rank,
    get_neighboring_cities_in_region_by_visits_rank,
)
from city.services.interfaces import AbstractVisitedCityService
from collection.models import Collection
from services import logger


class VisitedCityService(AbstractVisitedCityService):
    MONTH_NAMES = [
        '',
        'Январь',
        'Февраль',
        'Март',
        'Апрель',
        'Май',
        'Июнь',
        'Июль',
        'Август',
        'Сентябрь',
        'Октябрь',
        'Ноябрь',
        'Декабрь',
    ]

    def __init__(
        self,
        city_repo: AbstractCityRepository,
        visited_city_repo: AbstractVisitedCityRepository,
        request: HttpRequest,
    ):
        self.city_repo = city_repo
        self.visited_city_repo = visited_city_repo
        self.request = request

    def get_city_details(self, city_id: int, user: AbstractBaseUser) -> CityDetailsDTO:
        try:
            city = self.city_repo.get_by_id(city_id)
        except City.DoesNotExist:
            logger.warning(
                self.request,
                f'(Visited city) Attempt to access a non-existent city #{city_id}',
            )
            raise Http404

        country_id = city.country.id

        # --- Средний рейтинг ---
        average_rating = self.visited_city_repo.get_average_rating(city)

        # --- Популярные месяцы ---
        popular_months = sorted(
            set(
                self.MONTH_NAMES[month] for month in self.visited_city_repo.get_popular_months(city)
            ),
            key=lambda m: self.MONTH_NAMES.index(m),
        )

        # --- Коллекции ---
        collections = list(Collection.objects.filter(city=city))

        # --- Количество посещений города пользователем ---
        number_of_visits = (
            self.visited_city_repo.count_user_visits(city, user) if user.is_authenticated else 0
        )

        # --- Общее число посещений всеми пользователями ---
        number_of_visits_all_users = self.visited_city_repo.count_all_visits(city)

        # --- Посещения пользователя ---
        visits = self.visited_city_repo.get_user_visits(city, user) if user.is_authenticated else []

        logger.info(self.request, f'(Visited city) Viewing the visited city #{city_id}')

        ####
        number_of_users_who_visit_city = get_number_of_users_who_visit_city(city_id)
        total_number_of_visits = get_total_number_of_visits()
        all_cities_qty = get_number_of_cities()
        region_cities_qty = get_number_of_cities_in_region_by_city(city_id)
        visits_rank_in_country = get_rank_by_visits_of_city(city_id, country_id)
        users_rank_in_country = get_rank_by_users_of_city(city_id, country_id)
        visits_rank_in_region = get_rank_by_visits_of_city_in_region(city_id, True)
        users_rank_in_region = get_rank_by_users_of_city_in_region(city_id, True)
        users_rank_in_country_neighboring_cities = get_neighboring_cities_by_users_rank(
            city_id, country_id
        )
        visits_rank_in_country_neighboring_cities = get_neighboring_cities_by_visits_rank(
            city_id, country_id
        )
        users_rank_neighboring_cities_in_region = get_neighboring_cities_in_region_by_users_rank(
            city_id, country_id
        )
        visits_rank_neighboring_cities_in_region = get_neighboring_cities_in_region_by_visits_rank(
            city_id, country_id
        )

        return CityDetailsDTO(
            city=city,
            average_rating=average_rating,
            popular_months=popular_months,
            visits=visits,
            collections=collections,
            number_of_visits=number_of_visits,
            number_of_visits_all_users=number_of_visits_all_users,
            number_of_users_who_visit_city=number_of_users_who_visit_city,
            total_number_of_visits=total_number_of_visits,
            all_cities_qty=all_cities_qty,
            region_cities_qty=region_cities_qty,
            visits_rank_in_country=visits_rank_in_country,
            users_rank_in_country=users_rank_in_country,
            visits_rank_in_region=visits_rank_in_region,
            users_rank_in_region=users_rank_in_region,
            users_rank_in_country_neighboring_cities=users_rank_in_country_neighboring_cities,
            visits_rank_in_country_neighboring_cities=visits_rank_in_country_neighboring_cities,
            users_rank_neighboring_cities_in_region=users_rank_neighboring_cities_in_region,
            visits_rank_neighboring_cities_in_region=visits_rank_neighboring_cities_in_region,
        )
