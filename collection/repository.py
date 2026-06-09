"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import uuid
from collections import defaultdict
from typing import Any, Iterable

from django.contrib.auth.models import User
from django.db.models import (
    Count,
    Exists,
    F,
    IntegerField,
    OuterRef,
    Prefetch,
    Q,
    QuerySet,
    Subquery,
    Value,
    Window,
)
from django.db.models.functions import Coalesce, RowNumber

from city.models import City, VisitedCity
from collection.models import Collection, FavoriteCollection, PersonalCollection

# Сколько городов показываем в карточке коллекции на странице списка.
COLLECTION_LIST_PREVIEW_CITIES_LIMIT = 10


class CollectionRepository:
    """
    Репозиторий для работы с коллекциями в базе данных.
    """

    @staticmethod
    def _collection_city_count_subquery() -> Subquery:
        """
        Подзапрос: число городов в коллекции без JOIN-раздувания основной выборки.
        """
        through = Collection.city.through
        city_count_queryset = (
            through.objects.filter(collection_id=OuterRef('pk'))
            .values('collection_id')
            .annotate(city_count=Count('city_id'))  # type: ignore[misc]
            .values('city_count')[:1]
        )
        return Subquery(
            city_count_queryset,
            output_field=IntegerField(),
        )

    @staticmethod
    def _collection_visited_city_count_subquery(user: User) -> Subquery:
        """
        Подзапрос: число посещённых городов коллекции для пользователя.
        """
        through = Collection.city.through
        visited_count_queryset = (
            through.objects.filter(
                collection_id=OuterRef('pk'),
                city__visitedcity__user=user,
                city__visitedcity__is_first_visit=True,
            )
            .values('collection_id')
            .annotate(visited_count=Count('city_id', distinct=True))  # type: ignore[misc]
            .values('visited_count')[:1]
        )
        return Subquery(
            visited_count_queryset,
            output_field=IntegerField(),
        )

    def get_collections_with_annotations(
        self, user: User | None = None
    ) -> QuerySet[Collection, Any]:
        """
        Возвращает QuerySet коллекций с аннотациями:
        - qty_of_cities: количество городов в коллекции
        - qty_of_visited_cities: количество посещённых городов (для авторизованных пользователей)
        - is_favorite: находится ли коллекция в избранном (для авторизованных пользователей)

        Счётчики считаются коррелированными подзапросами по M2M-таблице, а не через
        LEFT JOIN + GROUP BY по всем городам и посещениям (иначе PostgreSQL раздувает строки).

        :param user: Пользователь для которого нужно вычислить аннотации. Если None, то аннотации для неавторизованных.
        :return: QuerySet коллекций с аннотациями.
        """
        annotations: dict[str, Any] = {
            'qty_of_cities': Coalesce(
                self._collection_city_count_subquery(),
                Value(0),
                output_field=IntegerField(),
            ),
        }

        if user and user.is_authenticated:
            favorite_subquery = FavoriteCollection.objects.filter(
                user=user, collection=OuterRef('pk')
            )
            annotations['qty_of_visited_cities'] = Coalesce(
                self._collection_visited_city_count_subquery(user),
                Value(0),
                output_field=IntegerField(),
            )
            annotations['is_favorite'] = Exists(favorite_subquery)

        # Города для карточек подгружаются отдельно (attach_preview_cities).
        return Collection.objects.annotate(**annotations)

    def get_collection_list_statistics(
        self,
        user: User | None = None,
    ) -> dict[str, int]:
        """
        Считает агрегированную статистику по коллекциям без тяжёлого aggregate()
        по аннотированному queryset.

        Для авторизованных пользователей используются лёгкие EXISTS-проверки
        по M2M-таблице вместо JOIN всех городов и посещений.
        """
        qty_of_collections = Collection.objects.count()

        if not user or not user.is_authenticated:
            return {
                'qty_of_collections': qty_of_collections,
                'qty_of_started_collections': 0,
                'qty_of_finished_collections': 0,
            }

        through = Collection.city.through
        has_cities_in_collection = through.objects.filter(collection_id=OuterRef('pk'))
        visited_in_collection = through.objects.filter(
            collection_id=OuterRef('pk'),
            city__visitedcity__user=user,
            city__visitedcity__is_first_visit=True,
        )
        unvisited_in_collection = through.objects.filter(
            collection_id=OuterRef('pk'),
        ).exclude(
            city__visitedcity__user=user,
            city__visitedcity__is_first_visit=True,
        )

        return {
            'qty_of_collections': qty_of_collections,
            'qty_of_started_collections': Collection.objects.filter(
                Exists(visited_in_collection)
            ).count(),
            # Пустая коллекция (0 городов) не считается завершённой: ~Exists(unvisited)
            # истинно при отсутствии строк в M2M, поэтому требуем хотя бы один город.
            'qty_of_finished_collections': Collection.objects.filter(
                Exists(has_cities_in_collection),
                ~Exists(unvisited_in_collection),
            ).count(),
        }

    def attach_preview_cities(
        self,
        collections: Iterable[Collection],
        user: User | None = None,
        limit: int = COLLECTION_LIST_PREVIEW_CITIES_LIMIT,
    ) -> None:
        """
        Подгружает первые `limit` городов для каждой коллекции на текущей странице.

        Вместо prefetch_related('city') по всем городам коллекции используется
        оконная функция ROW_NUMBER() — в выборку попадает не более `limit` городов
        на коллекцию. Для авторизованных пользователей каждый город получает
        атрибут is_visited через Exists-подзапрос.
        """
        collection_ids = [collection.pk for collection in collections]
        if not collection_ids:
            return

        through = Collection.city.through
        ranked_links: QuerySet[Any, Any] = (
            through.objects.filter(collection_id__in=collection_ids)
            .annotate(
                row_num=Window(
                    expression=RowNumber(),
                    partition_by=[F('collection_id')],
                    order_by=F('city__title').asc(),
                )
            )
            .filter(row_num__lte=limit)  # type: ignore[misc]
            .select_related('city')
        )

        if user and user.is_authenticated:
            visited_subquery = VisitedCity.objects.filter(
                user=user,
                city_id=OuterRef('city_id'),
                is_first_visit=True,
            )
            ranked_links = ranked_links.annotate(is_visited=Exists(visited_subquery))

        cities_by_collection: dict[int, list[City]] = defaultdict(list)
        for link in ranked_links:
            city = link.city
            is_visited = (
                bool(getattr(link, 'is_visited', False))
                if user and user.is_authenticated
                else False
            )
            setattr(city, 'is_visited', is_visited)
            cities_by_collection[link.collection_id].append(city)

        for collection in collections:
            setattr(collection, 'preview_cities', cities_by_collection.get(collection.pk, []))

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

    def get_public_collections_with_annotations(
        self,
    ) -> QuerySet[PersonalCollection, Any]:
        """
        Возвращает QuerySet публичных персональных коллекций всех пользователей с аннотациями:
        - qty_of_cities: количество городов в коллекции
        - first_15_cities: первые 15 городов по алфавиту (через prefetch с to_attr)

        :return: QuerySet публичных персональных коллекций с аннотациями, отсортированный по дате создания (новые первыми).
        """
        cities_prefetch = Prefetch(
            'city',
            queryset=City.objects.order_by('title'),
            to_attr='first_15_cities',
        )
        return (
            PersonalCollection.objects.filter(is_public=True)
            .select_related('user')
            .prefetch_related(cities_prefetch)
            .annotate(
                qty_of_cities=Count('city', distinct=True),
            )
            .order_by('-created_at')
        )
