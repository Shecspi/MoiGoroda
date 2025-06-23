from abc import ABC, abstractmethod

from django.contrib.auth.base_user import AbstractBaseUser

from city.models import City
from typing import Sequence


class AbstractCityRepository(ABC):
    @abstractmethod
    def get_by_id(self, city_id: int) -> City:
        pass


class AbstractVisitedCityRepository(ABC):
    @abstractmethod
    def get_average_rating(self, city: City) -> float:
        pass

    @abstractmethod
    def count_user_visits(self, city: City, user: AbstractBaseUser) -> int:
        pass

    @abstractmethod
    def count_all_visits(self, city_id: int) -> int:
        pass

    @abstractmethod
    def get_popular_months(self, city: City) -> list[int]:
        pass

    @abstractmethod
    def get_user_visits(self, city: City, user: AbstractBaseUser) -> Sequence[dict]:
        pass
