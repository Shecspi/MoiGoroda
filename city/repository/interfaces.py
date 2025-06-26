from abc import ABC, abstractmethod

from django.contrib.auth.base_user import AbstractBaseUser

from city.models import City
from typing import Sequence


class AbstractCityRepository(ABC):
    @abstractmethod
    def get_by_id(self, city_id: int) -> City:
        pass

    @abstractmethod
    def get_number_of_cities(self, country_code: str | None = None) -> int:
        pass

    @abstractmethod
    def get_number_of_cities_in_region_by_city(self, city_id: int) -> int:
        pass

    @abstractmethod
    def get_rank_in_country_by_visits(self, city_id: int) -> int:
        pass

    @abstractmethod
    def get_rank_in_country_by_users(self, city_id) -> int:
        pass

    @abstractmethod
    def get_rank_in_region_by_visits(self, city_id: int) -> int:
        pass

    @abstractmethod
    def get_rank_in_region_by_users(self, city_id: int) -> int:
        pass

    @abstractmethod
    def get_neighboring_cities_by_rank_in_region_by_users(self, city_id: int) -> list[City]:
        pass

    @abstractmethod
    def get_neighboring_cities_by_rank_in_region_by_visits(self, city_id: int) -> list[City]:
        pass

    @abstractmethod
    def get_neighboring_cities_by_rank_in_country_by_visits(self, city_id: int) -> list[City]:
        pass

    @abstractmethod
    def get_neighboring_cities_by_rank_in_country_by_users(self, city_id: int) -> list[City]:
        pass


class AbstractVisitedCityRepository(ABC):
    @abstractmethod
    def get_average_rating(self, city_id: int) -> float:
        pass

    @abstractmethod
    def count_user_visits(self, city_id: int, user: AbstractBaseUser) -> int:
        pass

    @abstractmethod
    def count_all_visits(self, city_id: int) -> int:
        pass

    @abstractmethod
    def get_popular_months(self, city_id: int) -> list[int]:
        pass

    @abstractmethod
    def get_user_visits(self, city_id: int, user: AbstractBaseUser) -> Sequence[dict]:
        pass

    @abstractmethod
    def get_number_of_users_who_visit_city(self, city_id: int) -> int:
        pass
