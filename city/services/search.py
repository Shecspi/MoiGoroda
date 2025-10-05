"""
Сервис для поиска городов.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.db.models import QuerySet, Case, When, IntegerField

from city.models import City


class CitySearchService:
    """Сервис для поиска городов."""

    @staticmethod
    def search_cities(query: str, country: str | None = None, limit: int = 50) -> QuerySet[City]:
        """
        Поиск городов по подстроке с дополнительными фильтрами.

        :param query: Подстрока для поиска в названии города
        :param country: Код страны для дополнительной фильтрации
        :param limit: Максимальное количество результатов (по умолчанию 50)
        :return: QuerySet с найденными городами
        """
        # Базовый запрос с оптимизацией и приоритизацией
        cities_queryset = (
            City.objects.select_related('region__country')
            .filter(title__icontains=query)
            .annotate(
                # Приоритет для городов, начинающихся с поискового запроса
                search_priority=Case(
                    When(title__istartswith=query, then=1),
                    default=2,
                    output_field=IntegerField(),
                )
            )
            .order_by('search_priority', 'title')
        )

        # Дополнительная фильтрация по стране
        if country:
            cities_queryset = cities_queryset.filter(region__country__code=country)

        # Ограничиваем количество результатов для производительности
        return cities_queryset[:limit]
