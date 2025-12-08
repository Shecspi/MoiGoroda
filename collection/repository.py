"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import uuid
from typing import Any

from django.contrib.auth.models import User
from django.db.models import Count, Exists, OuterRef, Q, QuerySet

from city.models import VisitedCity
from collection.models import Collection, FavoriteCollection, PersonalCollection


class CollectionRepository:
    """
    Репозиторий для работы с коллекциями в базе данных.
    """

    def get_collections_with_annotations(
        self, user: User | None = None
    ) -> QuerySet[Collection, Any]:
        """
        Возвращает QuerySet коллекций с аннотациями:
        - qty_of_cities: количество городов в коллекции
        - qty_of_visited_cities: количество посещённых городов (для авторизованных пользователей)
        - is_favorite: находится ли коллекция в избранном (для авторизованных пользователей)

        :param user: Пользователь для которого нужно вычислить аннотации. Если None, то аннотации для неавторизованных.
        :return: QuerySet коллекций с аннотациями.
        """
        if user and user.is_authenticated:
            favorite_subquery = FavoriteCollection.objects.filter(
                user=user, collection=OuterRef('pk')
            )

            return Collection.objects.prefetch_related('city').annotate(
                qty_of_cities=Count('city', distinct=True),
                qty_of_visited_cities=Count(
                    'city__visitedcity',
                    filter=Q(
                        city__visitedcity__user=user,
                        city__visitedcity__is_first_visit=True,
                    ),
                ),
                is_favorite=Exists(favorite_subquery),
            )
        else:
            return Collection.objects.prefetch_related('city').annotate(
                qty_of_cities=Count('city', distinct=True)
            )

    def get_visited_city_ids(self, user: User) -> QuerySet[Any, Any]:
        """
        Возвращает QuerySet с ID городов, которые посещены пользователем.

        :param user: Пользователь, для которого нужно получить список посещённых городов.
        :return: QuerySet с ID посещённых городов.
        """
        return VisitedCity.objects.filter(user=user).values_list('city__id', flat=True)

    def get_personal_collections_with_annotations(
        self, user: User
    ) -> QuerySet[PersonalCollection, Any]:
        """
        Возвращает QuerySet персональных коллекций пользователя с аннотациями:
        - qty_of_cities: количество городов в коллекции
        - qty_of_visited_cities: количество посещённых городов

        :param user: Пользователь, чьи персональные коллекции нужно получить.
        :return: QuerySet персональных коллекций с аннотациями, отсортированный по дате создания (новые первыми).
        """
        return (
            PersonalCollection.objects.filter(user=user)
            .prefetch_related('city')
            .annotate(
                qty_of_cities=Count('city', distinct=True),
                qty_of_visited_cities=Count(
                    'city__visitedcity',
                    filter=Q(
                        city__visitedcity__user=user,
                        city__visitedcity__is_first_visit=True,
                    ),
                    distinct=True,
                ),
            )
            .order_by('-created_at')
        )

    def get_personal_collection_by_id(self, collection_id: uuid.UUID) -> PersonalCollection:
        """
        Возвращает персональную коллекцию по ID.

        :param collection_id: UUID персональной коллекции.
        :return: Объект PersonalCollection.
        :raises ObjectDoesNotExist: Если коллекция не найдена.
        """
        return PersonalCollection.objects.get(id=collection_id)
