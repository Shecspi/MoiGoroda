from typing import Any

from django.db.models import Count, Window, F
from django.db.models.functions import Rank

from city.models import City
from city.repository.interfaces import AbstractCityRepository


class CityRepository(AbstractCityRepository):
    def __init__(self) -> None:
        self._city_cache: dict[int, City] = {}
        self._rank_cache: dict[str, list[dict[str, Any]]] = {}

    def get_by_id(self, city_id: int) -> City:
        """
        Возвращает экземпляр модели City, соответствующий указанному city_id.
        """
        if city_id not in self._city_cache:
            self._city_cache[city_id] = City.objects.get(id=city_id)
        return self._city_cache[city_id]

    def get_number_of_cities(self, country_code: str | None = None) -> int:
        """
        Возвращает количество городов, сохранённых в базе данных.
        """
        queryset = City.objects.all()
        if country_code:
            queryset = queryset.filter(country__code=country_code)
        return queryset.count()

    def get_number_of_cities_in_region_by_city(self, city_id: int) -> int:
        """
        Возвращает количество городов в том же регионе, в котором находится город с city_id.
        """
        try:
            city = self.get_by_id(city_id)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            return 0

        return City.objects.filter(region=city.region).count()

    def get_rank_in_country_by_visits(self, city_id: int) -> int:
        ranked_cities = self._get_ranked_cities_by_country_visits(city_id)
        return self._extract_rank(ranked_cities, city_id)

    def get_rank_in_country_by_users(self, city_id: int) -> int:
        ranked_cities = self._get_ranked_cities_by_country_users(city_id)
        return self._extract_rank(ranked_cities, city_id)

    def get_rank_in_region_by_visits(self, city_id: int) -> int:
        """
        Возвращает местоположение города в рейтинге городов региона на основе количества посещений.
        Если в стране есть разбивка на регионы, то показывает рейтинг в этом регионе.
        Если такой разбивки нет, то в рейтинг пойдут все города страны.
        """
        ranked_cities = self._get_ranked_cities_by_region_visits(city_id)
        return self._extract_rank(ranked_cities, city_id)

    def get_rank_in_region_by_users(self, city_id: int) -> int:
        """
        Возвращает местоположение города в рейтинге городов региона на основе количества пользователей, посетивших город.
        Если в стране есть разбивка на регионы, то показывает рейтинг в этом регионе.
        Если такой разбивки нет, то в рейтинг пойдут все города страны.
        """
        ranked_cities = self._get_ranked_cities_by_region_users(city_id)
        return self._extract_rank(ranked_cities, city_id)

    def get_neighboring_cities_by_rank_in_region_by_users(
        self, city_id: int
    ) -> list[dict[str, Any]]:
        """
        Возвращает список 10 городов по стране, которые располагаются близко к искомому городу.
        Выборка происходит по общему количеству пользователей, посетивших город.
        """
        ranked_cities = self._get_ranked_cities_by_region_users(city_id)
        return self._get_cities_near_index(ranked_cities, city_id)

    def get_neighboring_cities_by_rank_in_region_by_visits(
        self, city_id: int
    ) -> list[dict[str, Any]]:
        """
        Возвращает список 10 городов по стране, которые располагаются близко к искомому городу.
        Выборка происходит по количеству посещений города всеми пользователями.
        """
        ranked_cities = self._get_ranked_cities_by_region_visits(city_id)
        return self._get_cities_near_index(ranked_cities, city_id)

    def get_neighboring_cities_by_rank_in_country_by_visits(
        self, city_id: int
    ) -> list[dict[str, Any]]:
        """
        Возвращает список 10 городов по стране, которые располагаются близко к искомому городу.
        Выборка происходит по количеству посещений города всеми пользователями.
        """
        ranked_cities = self._get_ranked_cities_by_country_visits(city_id)
        return self._get_cities_near_index(ranked_cities, city_id)

    def get_neighboring_cities_by_rank_in_country_by_users(
        self, city_id: int
    ) -> list[dict[str, Any]]:
        """
        Возвращает список 10 городов по стране, которые располагаются близко к искомому городу.
        Выборка происходит по общему количеству пользователей, посетивших город.
        """
        ranked_cities = self._get_ranked_cities_by_country_users(city_id)
        return self._get_cities_near_index(ranked_cities, city_id)

    @staticmethod
    def _get_cities_near_index(items: list[dict[str, Any]], city_id: int) -> list[dict[str, Any]]:
        # Ищем индекс нужного города
        index = next((i for i, city in enumerate(items) if city['id'] == city_id), None)
        if index is None:
            return []

        # Выбираем 10 соседних городов
        start = max(index - 4, 0)
        end = start + 10
        if end > len(items):
            end = len(items)
            start = max(0, end - 10)

        return items[start:end]

    @staticmethod
    def _extract_rank(ranked_cities: list[dict[str, Any]], city_id: int) -> int:
        for city_dict in ranked_cities:
            if isinstance(city_dict, dict) and city_dict.get('id') == city_id:
                rank = city_dict.get('rank')
                return int(rank) if rank is not None else 0
        return 0

    def _get_ranked_cities_by_country_visits(self, city_id: int) -> list[dict[str, Any]]:
        cache_key = f'country_visits_{city_id}'
        if cache_key not in self._rank_cache:
            try:
                city = self.get_by_id(city_id)
            except (City.DoesNotExist, City.MultipleObjectsReturned):
                return []

            self._rank_cache[cache_key] = list(
                City.objects.all()
                .filter(country_id=city.country.id)
                .annotate(
                    visits=Count('visitedcity'),
                    rank=Window(expression=Rank(), order_by=F('visits').desc()),
                )
                .values('id', 'title', 'visits', 'rank')
                .order_by('rank')
            )
        return self._rank_cache[cache_key]

    def _get_ranked_cities_by_country_users(self, city_id: int) -> list[dict[str, Any]]:
        cache_key = f'country_users_{city_id}'
        if cache_key not in self._rank_cache:
            try:
                city = self.get_by_id(city_id)
            except (City.DoesNotExist, City.MultipleObjectsReturned):
                return []

            self._rank_cache[cache_key] = list(
                City.objects.filter(country_id=city.country.id)
                .annotate(
                    visits=Count('visitedcity__user', distinct=True),
                    rank=Window(expression=Rank(), order_by=F('visits').desc()),
                )
                .values('id', 'title', 'visits', 'rank')
                .order_by('rank')
            )
        return self._rank_cache[cache_key]

    def _get_ranked_cities_by_region_visits(self, city_id: int) -> list[dict[str, Any]]:
        cache_key = f'region_visits_{city_id}'
        if cache_key not in self._rank_cache:
            try:
                city = self.get_by_id(city_id)
            except (City.DoesNotExist, City.MultipleObjectsReturned):
                return []

            if city.region:
                queryset = City.objects.select_related('region').filter(region=city.region)
            else:
                queryset = City.objects.select_related('country').filter(country=city.country)

            self._rank_cache[cache_key] = list(
                queryset.annotate(
                    visits=Count('visitedcity'),
                    rank=Window(expression=Rank(), order_by=F('visits').desc()),
                )
                .values('id', 'title', 'visits', 'rank')
                .order_by('rank')
            )
        return self._rank_cache[cache_key]

    def _get_ranked_cities_by_region_users(self, city_id: int) -> list[dict[str, Any]]:
        cache_key = f'region_users_{city_id}'
        if cache_key not in self._rank_cache:
            try:
                city = self.get_by_id(city_id)
            except (City.DoesNotExist, City.MultipleObjectsReturned):
                return []

            if city.region:
                queryset = City.objects.select_related('region').filter(region=city.region)
            else:
                queryset = City.objects.select_related('country').filter(country=city.country)

            self._rank_cache[cache_key] = list(
                queryset.annotate(
                    visits=Count('visitedcity__user', distinct=True),
                    rank=Window(expression=Rank(), order_by=F('visits').desc()),
                )
                .values('id', 'title', 'visits', 'rank')
                .order_by('rank')
            )
        return self._rank_cache[cache_key]
