from django.db.models import Count, Window, F
from django.db.models.functions import Rank

from city.models import City
from city.repository.interfaces import AbstractCityRepository


class CityRepository(AbstractCityRepository):
    def get_by_id(self, city_id: int) -> City:
        """
        Возвращает экземпляр модели City, соответствующий указанному city_id.
        """
        return City.objects.get(id=city_id)

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
            city = City.objects.get(id=city_id)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            return 0

        return City.objects.filter(region=city.region).count()

    def get_rank_in_country_by_visits(self, city_id: int) -> int:
        city = self.get_by_id(city_id)
        queryset = City.objects.filter(country_id=city.country.id)

        ranked_cities = list(
            queryset.annotate(
                visits=Count('visitedcity'),
                rank=Window(expression=Rank(), order_by=F('visits').desc()),
            )
            .values('id', 'title', 'visits', 'rank')
            .order_by('rank')
        )

        for city in ranked_cities:
            if city['id'] == city_id:
                return city['rank']

        return 0

    def get_rank_in_country_by_users(self, city_id) -> int:
        ranked_cities = list(
            City.objects.annotate(
                visits=Count('visitedcity__user', distinct=True),
                rank=Window(
                    expression=Rank(), partition_by=F('country'), order_by=F('visits').desc()
                ),
            )
            .values('id', 'title', 'visits', 'rank')
            .order_by('rank')
        )

        for city in ranked_cities:
            if city['id'] == city_id:
                return city['rank']

        return 0

    def get_rank_in_region_by_visits(self, city_id: int) -> int:
        """
        Возвращает местоположение города в рейтинге городов региона на основе количества посещений.
        Если в стране есть разбивка на регионы, то показывает рейтинг в этом регионе.
        Если такой разбивки нет, то в рейтинг пойдут все города страны.
        """
        try:
            city = City.objects.get(id=city_id)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            return 0

        if city.region:
            queryset = City.objects.select_related('region').filter(region=city.region)
        else:
            queryset = City.objects.select_related('country').filter(country=city.country)

        ranked_cities = list(
            queryset.annotate(
                visits=Count('visitedcity'),
                rank=Window(expression=Rank(), order_by=F('visits').desc()),
            )
            .values('id', 'title', 'visits', 'rank')
            .order_by('rank')
        )

        for city in ranked_cities:
            if city['id'] == city_id:
                return city['rank']

        return 0

    def get_rank_in_region_by_users(self, city_id: int) -> int:
        """
        Возвращает местоположение города в рейтинге городов региона на основе количества пользователей, посетивших город.
        Если в стране есть разбивка на регионы, то показывает рейтинг в этом регионе.
        Если такой разбивки нет, то в рейтинг пойдут все города страны.
        """
        try:
            city = City.objects.get(id=city_id)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            return 0

        if city.region:
            queryset = City.objects.select_related('region').filter(region=city.region)
        else:
            queryset = City.objects.select_related('country').filter(country=city.country)

        ranked_cities = list(
            queryset.annotate(
                visits=Count('visitedcity__user', distinct=True),
                rank=Window(expression=Rank(), order_by=F('visits').desc()),
            )
            .values('id', 'title', 'visits', 'rank')
            .order_by('rank')
        )

        for city in ranked_cities:
            if city['id'] == city_id:
                return city['rank']

        return 0

    # Нет тестов
    def get_neighboring_cities_by_rank_in_region_by_users(self, city_id: int) -> list[City]:
        """
        Возвращает список 10 городов по стране, которые располагаются близко к искомому городу.
        Выборка происходит по общему количеству пользователей, посетивших город.
        """
        try:
            city = City.objects.get(id=city_id)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            return []

        if city.region:
            queryset = City.objects.select_related('region').filter(region_id=city.region.id)
        else:
            queryset = City.objects.select_related('country').filter(country_id=city.country.id)

        ranked_cities = list(
            queryset.annotate(
                visits=Count('visitedcity'),
                rank=Window(expression=Rank(), order_by=F('visits').desc()),
            )
            .values('id', 'title', 'visits', 'rank')
            .order_by('rank')
        )
        return self._get_cities_near_index(ranked_cities, city_id)

    # Нет тестов
    def get_neighboring_cities_by_rank_in_region_by_visits(self, city_id: int) -> list[City]:
        """
        Возвращает список 10 городов по стране, которые располагаются близко к искомому городу.
        Выборка происходит по количеству посещений города всеми пользователями.
        """
        try:
            city = City.objects.get(id=city_id)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            return []

        if city.region:
            queryset = City.objects.select_related('region').filter(region_id=city.region.id)
        else:
            queryset = City.objects.select_related('country').filter(country_id=city.country.id)

        ranked_cities = list(
            queryset.annotate(
                visits=Count('visitedcity__user', distinct=True),
                rank=Window(expression=Rank(), order_by=F('visits').desc()),
            )
            .values('id', 'title', 'visits', 'rank')
            .order_by('rank')
        )
        return self._get_cities_near_index(ranked_cities, city_id)

    # Нет тестов
    def get_neighboring_cities_by_rank_in_country_by_visits(self, city_id: int) -> list[City]:
        """
        Возвращает список 10 городов по стране, которые располагаются близко к искомому городу.
        Выборка происходит по количеству посещений города всеми пользователями.
        """
        try:
            city = City.objects.get(id=city_id)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            return []

        ranked_cities = list(
            City.objects.all()
            .filter(country_id=city.country.id)
            .annotate(
                visits=Count('visitedcity'),
                rank=Window(expression=Rank(), order_by=F('visits').desc()),
            )
            .values('id', 'title', 'visits', 'rank')
            .order_by('rank')
        )
        return self._get_cities_near_index(ranked_cities, city_id)

    # Нет тестов
    def get_neighboring_cities_by_rank_in_country_by_users(self, city_id: int) -> list[City]:
        """
        Возвращает список 10 городов по стране, которые располагаются близко к искомому городу.
        Выборка происходит по общему количеству пользователей, посетивших город.
        """
        try:
            city = City.objects.get(id=city_id)
        except (City.DoesNotExist, City.MultipleObjectsReturned):
            return []

        ranked_cities = list(
            City.objects.filter(country_id=city.country.id)
            .annotate(
                visits=Count('visitedcity__user', distinct=True),
                rank=Window(expression=Rank(), order_by=F('visits').desc()),
            )
            .values('id', 'title', 'visits', 'rank')
            .order_by('rank')
        )
        return self._get_cities_near_index(ranked_cities, city_id)

    @staticmethod
    def _get_cities_near_index(items: list, city_id: int) -> list:
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
