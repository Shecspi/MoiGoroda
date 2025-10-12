from dataclasses import dataclass
from typing import Any, Sequence

from city.models import City
from collection.models import Collection


@dataclass
class CityDetailsDTO:
    city: City
    average_rating: float
    popular_months: list[str]
    visits: Sequence[dict[str, Any]]
    collections: list[Collection]
    # Количество
    number_of_visits: int
    number_of_visits_all_users: int
    number_of_users_who_visit_city: int
    number_of_cities_in_country: int
    number_of_cities_in_region: int
    # Ранги
    rank_in_country_by_visits: int
    rank_in_country_by_users: int
    rank_in_region_by_visits: int
    rank_in_region_by_users: int
    neighboring_cities_by_rank_in_country_by_visits: list[dict[str, Any]]
    neighboring_cities_by_rank_in_country_by_users: list[dict[str, Any]]
    neighboring_cities_by_rank_in_region_by_visits: list[dict[str, Any]]
    neighboring_cities_by_rank_in_region_by_users: list[dict[str, Any]]

    @property
    def page_title(self) -> str:
        if self.city.region:
            return f'{self.city.title}, {self.city.region}, {self.city.country} - информация о городе, карта'
        return f'{self.city.title}, {self.city.country} - информация о городе, карта'

    @property
    def page_description(self) -> str:
        if self.city.region:
            desc = f'{self.city.title}, {self.city.region}, {self.city.country}. '
        else:
            desc = f'{self.city.title}, {self.city.country}. '

        if len(self.collections) == 1:
            desc += f'Входит в коллекцию «{self.collections[0]}». '
        elif len(self.collections) >= 2:
            desc += (
                f'Входит в коллекции {", ".join(["«" + str(c) + "»" for c in self.collections])}. '
            )

        if self.average_rating:
            desc += f'Средняя оценка путешественников — {self.average_rating}. '

        if self.popular_months:
            months = ', '.join(self.popular_months)
            desc += f'Лучшее время для поездки: {months}. '

        desc += (
            'Смотрите информацию о городе и карту на сайте «Мои Города». '
            'Зарегистрируйтесь, чтобы отмечать посещённые города.'
        )

        return desc
