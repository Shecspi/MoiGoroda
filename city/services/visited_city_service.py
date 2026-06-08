from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest, Http404

from city.dto import CityDetailsDTO
from city.models import City
from city.repository.interfaces import AbstractCityRepository, AbstractVisitedCityRepository
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
        vc_repo = self.visited_city_repo

        try:
            city = self.city_repo.get_by_id(city_id)
        except City.DoesNotExist:
            logger.warning(
                self.request,
                f'(Visited city) Attempt to access a non-existent city #{city_id}',
            )
            raise Http404

        # --- Средний рейтинг ---
        average_rating = vc_repo.get_average_rating(city_id)

        # --- Популярные месяцы ---
        popular_months = sorted(
            set(self.MONTH_NAMES[month] for month in vc_repo.get_popular_months(city_id)),
            key=lambda m: self.MONTH_NAMES.index(m),
        )

        # --- Коллекции ---
        collections = list(Collection.objects.filter(city=city))

        # --- Посещения пользователя ---
        visits = vc_repo.get_user_visits(city_id, user) if user.is_authenticated else []

        # --- Количество посещений города --
        number_of_visits = vc_repo.count_user_visits(city_id, user) if user.is_authenticated else 0
        number_of_visits_all_users = vc_repo.count_all_visits(city_id)
        number_of_users_who_visit_city = vc_repo.get_number_of_users_who_visit_city(city_id)

        logger.info(self.request, f'(Visited city) Viewing the visited city #{city_id}')

        return CityDetailsDTO(
            city=city,
            average_rating=average_rating,
            popular_months=popular_months,
            visits=visits,
            collections=collections,
            # Количество
            number_of_visits=number_of_visits,
            number_of_visits_all_users=number_of_visits_all_users,
            number_of_users_who_visit_city=number_of_users_who_visit_city,
        )
