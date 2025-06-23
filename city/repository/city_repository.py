from city.models import City
from city.repository.interfaces import AbstractCityRepository


class CityRepository(AbstractCityRepository):
    def get_by_id(self, city_id: int) -> City:
        return City.objects.get(id=city_id)
