from dataclasses import dataclass
from typing import Any

from city.models import City
from collection.models import Collection


@dataclass
class CityDetailsDTO:
    city: City
    average_rating: float
    popular_months: list[str]
    visits: list[dict[str, Any]]
    collections: list[Collection]
    number_of_visits: int
    number_of_visits_all_users: int
    number_of_users_who_visit_city: int
    total_number_of_visits: int
    all_cities_qty: int
    region_cities_qty: int
    visits_rank_in_country: int
    users_rank_in_country: int
    visits_rank_in_region: int
    users_rank_in_region: int
    users_rank_in_country_neighboring_cities: list[City]
    visits_rank_in_country_neighboring_cities: list[City]
    users_rank_neighboring_cities_in_region: list[City]
    visits_rank_neighboring_cities_in_region: list[City]

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
                f"Входит в коллекции {', '.join(['«' + str(c) + '»' for c in self.collections])}. "
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
