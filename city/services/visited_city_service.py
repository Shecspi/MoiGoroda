from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest, Http404

from city.dto import CityDetailsDTO
from city.models import City
from city.repository.interfaces import AbstractCityRepository, AbstractVisitedCityRepository
from collection.models import Collection
from services import logger


class VisitedCityService:
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

        return CityDetailsDTO(
            city=city,
            average_rating=average_rating,
            popular_months=popular_months,
            visits=visits,
            collections=collections,
            number_of_visits=number_of_visits,
            number_of_visits_all_users=number_of_visits_all_users,
        )
