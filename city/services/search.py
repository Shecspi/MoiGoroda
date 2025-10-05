"""
Сервис для поиска городов.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.db.models import QuerySet

from city.models import City


class CitySearchService:
    """Сервис для поиска городов."""

    @staticmethod
    def search_cities(query: str, country: str | None = None) -> QuerySet[City]:
        """
        Поиск городов по подстроке с дополнительными фильтрами.

        :param query: Подстрока для поиска в названии города
        :param country: Код страны для дополнительной фильтрации
        :return: QuerySet с найденными городами
        """
        # Базовый запрос с оптимизацией
        cities_queryset = (
            City.objects.select_related('region__country')
            .filter(title__icontains=query)
            .order_by('title')
        )

        # Дополнительная фильтрация по стране
        if country:
            cities_queryset = cities_queryset.filter(region__country__code=country)

        return cities_queryset
