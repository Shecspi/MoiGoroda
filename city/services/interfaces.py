from abc import ABC, abstractmethod

from django.contrib.auth.base_user import AbstractBaseUser

from city.dto import CityDetailsDTO


class AbstractVisitedCityService(ABC):
    @abstractmethod
    def get_city_details(self, city_id: int, user: AbstractBaseUser) -> CityDetailsDTO:
        pass
