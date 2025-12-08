"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json
import uuid
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Count,
    Exists,
    OuterRef,
    Q,
)
from django.http import Http404
from django.utils.safestring import mark_safe
from django.views.generic import ListView, TemplateView

from city.models import VisitedCity
from collection.filter import apply_filter_to_queryset
from collection.models import Collection, FavoriteCollection, PersonalCollection
from collection.services import (
    get_all_cities_from_collection,
    get_all_cities_from_personal_collection,
)
from services import logger
from services.word_modifications.city import modification__city
from services.word_modifications.visited import modification__visited
from utils.CollectionListMixin import CollectionListMixin


class CollectionList(CollectionListMixin, ListView):  # type: ignore[type-arg]
    model = Collection
    paginate_by = 16
    template_name = 'collection/list/page.html'

    def __init__(self) -> None:
        super().__init__()

        # Список ID городов из таблицы City, которые посещены пользователем
        self.visited_cities: Any = None
        self.sort: str = ''
        self.filter: str = ''
        self.qty_of_collections: int = 0
        self.qty_of_started_colelctions: int = 0
        self.qty_of_finished_colelctions: int = 0

    def get_queryset(self) -> Any:
        if self.request.user.is_authenticated:
            # Создаём подзапрос для проверки, находится ли коллекция в избранном
            favorite_subquery = FavoriteCollection.objects.filter(
                user=self.request.user, collection=OuterRef('pk')
            )

            queryset = Collection.objects.prefetch_related('city').annotate(
                qty_of_cities=Count('city', distinct=True),
                qty_of_visited_cities=Count(
                    'city__visitedcity',
                    filter=Q(
                        city__visitedcity__user=self.request.user,
                        city__visitedcity__is_first_visit=True,
                    ),
                ),
                is_favorite=Exists(favorite_subquery),
            )

            self.visited_cities = VisitedCity.objects.filter(user=self.request.user).values_list(
                'city__id', flat=True
            )
        else:
            queryset = Collection.objects.prefetch_related('city').annotate(
                qty_of_cities=Count('city', distinct=True)
            )  # type: ignore[assignment]

        logger.info(self.request, '(Collections) Viewing the collection list')

        # Обновление счётчиков коллекций
        self.qty_of_collections = queryset.count()
        if self.request.user.is_authenticated:
            for collection in queryset:
                if collection.qty_of_visited_cities > 0:
                    self.qty_of_started_colelctions += 1
                if collection.qty_of_visited_cities == collection.qty_of_cities:
                    self.qty_of_finished_colelctions += 1

        # Применение фильтра
        filter_value = self.request.GET.get('filter')
        self.filter = filter_value if filter_value else ''
        if self.filter:
            try:
                queryset = self.apply_filter_to_queryset(queryset, self.filter)
                logger.info(self.request, f"(Collections) Using the filter '{self.filter}'")
            except KeyError:
                self.filter = ''
                logger.warning(
                    self.request, f"(Collections) Unexpected value of the filter '{filter_value}'"
                )

        # Применение сортировки
        sort_value = self.request.GET.get('sort')
        if self.request.user.is_authenticated:
            self.sort = sort_value if sort_value else 'default_auth'
        else:
            self.sort = sort_value if sort_value else 'default_guest'

        try:
            queryset = self.apply_sort_to_queryset(queryset, self.sort)
            if sort_value:
                logger.info(self.request, f"(Collections) Using the sort '{self.sort}'")
        except KeyError:
            logger.warning(
                self.request, f"(Collections) Unexpected value of the sort '{sort_value}'"
            )
            self.sort = 'default_auth' if self.request.user.is_authenticated else 'default_guest'
            queryset = self.apply_sort_to_queryset(queryset, self.sort)

        return queryset

    def get_context_data(self, *, object_list: Any = None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['sort'] = self.sort
        context['filter'] = self.filter
        context['visited_cities'] = self.visited_cities  # Все коллекции, в которых находится город
        context['qty_of_collections'] = self.qty_of_collections
        context['qty_of_started_colelctions'] = self.qty_of_started_colelctions
        context['qty_of_finished_colelctions'] = self.qty_of_finished_colelctions

        # Получаем персональные коллекции пользователя
        if self.request.user.is_authenticated:
            from django.db.models import Count, Q

            personal_collections = (
                PersonalCollection.objects.filter(user=self.request.user)
                .prefetch_related('city')
                .annotate(
                    qty_of_cities=Count('city', distinct=True),
                    qty_of_visited_cities=Count(
                        'city__visitedcity',
                        filter=Q(
                            city__visitedcity__user=self.request.user,
                            city__visitedcity__is_first_visit=True,
                        ),
                        distinct=True,
                    ),
                )
                .order_by('-created_at')
            )
            context['personal_collections'] = personal_collections
        else:
            context['personal_collections'] = PersonalCollection.objects.none()

        context['active_page'] = 'collection'

        url_params_for_sort = (
            '' if self.sort == 'default_auth' or self.sort == 'default_guest' else self.sort
        )

        context['url_for_filter_not_started'] = self.get_url_params(
            'not_started' if self.filter != 'not_started' else '',
            url_params_for_sort,
        )
        context['url_for_filter_finished'] = self.get_url_params(
            'finished' if self.filter != 'finished' else '', url_params_for_sort
        )
        context['url_for_sort_name_down'] = self.get_url_params(self.filter, 'name_down')
        context['url_for_sort_name_up'] = self.get_url_params(self.filter, 'name_up')
        context['url_for_sort_progress_down'] = self.get_url_params(self.filter, 'progress_down')
        context['url_for_sort_progress_up'] = self.get_url_params(self.filter, 'progress_up')

        context['page_title'] = 'Коллекции городов'
        context['page_description'] = (
            'Города России, распределённые по различным коллекциям. Путешествуйте по России и закрывайте коллекции.'
        )

        return context


class CollectionSelected_List(ListView):  # type: ignore[type-arg]
    model = Collection
    paginate_by = 16

    list_or_map: str = 'list'

    def __init__(self, list_or_map: str) -> None:
        super().__init__()

        self.pk: int | None = None
        self.filter: str = ''
        self.cities: Any = None
        self.qty_of_cities: int | None = None
        self.collection_title: Any = ''
        self.list_or_map = list_or_map
        self.qty_of_visited_cities: int | None = None

    def get(self, *args: Any, **kwargs: Any) -> Any:
        self.pk = self.kwargs['pk']

        # При обращении к несуществующей коллекции выдаём 404
        # При этом в указанной коллекции может не быть посещённых городов, это ок
        try:
            self.collection_title = Collection.objects.get(id=self.pk)
        except ObjectDoesNotExist:
            logger.warning(
                self.request,
                f'(Collection #{self.pk}) Attempt to access a non-existent collection',
            )
            raise Http404

        return super().get(*args, **kwargs)

    def get_queryset(self) -> Any:
        """
        Получает из базы данных все города коллекции, как посещённые так и нет,
        и возвращает Queryset, состоящий из полей:
            * `id` - ID города
            * `title` - название города
            * `population` - население города
            * `date_of_foundation` - дата основания города
            * `coordinate_width` - широта
            * `coordinate_longitude` - долгота
            * `is_visited` - True,если город посещён

            Для авторизованных пользователей доступны дополнительные поля:
            * `visited_id` - ID посещённого города
            * `date_of_visit` - дата посещения
            * `has_magnet` - True, если имеется сувенир из города
            * `rating` - рейтинг от 1 до 5
        """
        self.cities = get_all_cities_from_collection(
            self.pk,  # type: ignore[arg-type]
            self.request.user if self.request.user.is_authenticated else None,
        )
        self.qty_of_visited_cities = sum([1 if city.is_visited else 0 for city in self.cities])
        self.qty_of_cities = len(self.cities)

        # Определяем фильтрацию
        if self.request.user.is_authenticated:
            filter_value = self.request.GET.get('filter')
            self.filter = filter_value if filter_value else ''
            if self.filter:
                try:
                    self.cities = apply_filter_to_queryset(self.cities, self.filter)
                except KeyError:
                    logger.warning(
                        self.request,
                        f'(Collection #{self.pk}) Unexpected value of the filter - {self.request.GET.get("filter")}',
                    )
                else:
                    logger.info(
                        self.request,
                        f"(Collection #{self.pk}) Using the filter '{self.filter}'",
                    )

        return self.cities

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Для карты передаём полные данные о городах, для списка - упрощённые
        if self.list_or_map == 'map':
            context['all_cities'] = self.cities
        else:
            cities_data = [
                {
                    'name': city.title,
                    'lat': float(str(city.coordinate_width).replace(',', '.')),
                    'lon': float(str(city.coordinate_longitude).replace(',', '.')),
                    'is_visited': city.is_visited,
                }
                for city in self.cities
            ]
            context['cities'] = mark_safe(json.dumps(cities_data))

        context['filter'] = self.filter

        context['qty_of_cities'] = self.qty_of_cities
        context['qty_of_visited_cities'] = self.qty_of_visited_cities

        if self.request.user.is_authenticated:
            qty = self.qty_of_visited_cities if self.qty_of_visited_cities is not None else 0
            context['change__city'] = modification__city(qty)
            context['change__visited'] = modification__visited(qty)
            context['url_for_filter_visited'] = get_url_params(
                'visited' if self.filter != 'visited' else ''
            )
            context['url_for_filter_not_visited'] = get_url_params(
                'not_visited' if self.filter != 'not_visited' else ''
            )

        context['pk'] = self.pk
        context['page_title'] = self.collection_title
        context['page_description'] = (
            f'Города России, представленные в коллекции "{self.collection_title}". '
            f'Путешествуйте по России и закрывайте коллекции.'
        )

        return context

    def get_template_names(self) -> list[str]:
        if self.list_or_map == 'list':
            return [
                'collection/selected/list/page.html',
            ]
        elif self.list_or_map == 'map':
            return [
                'collection/selected/map/page.html',
            ]
        return []


def get_url_params(filter_value: str | None) -> str:
    """
    Возвращает строку, пригодную для использования в URL-адресе после знака '?' с параметрами 'filter' и 'sort'
    @param filter_value: Значение фльтра, может быть пустой строкой.
    """
    valid_filters = ['visited', 'not_visited']

    if filter_value and filter_value in valid_filters:
        return f'filter={filter_value}'

    return ''


class PersonalCollectionCreate(LoginRequiredMixin, TemplateView):
    """
    Отображает страницу создания персональной коллекции.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Вся логика формы обрабатывается на фронтенде через JS.
    """

    template_name = 'collection/personal/create/page.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['active_page'] = 'collection'
        context['page_title'] = 'Создание персональной коллекции'
        context['page_description'] = 'Создайте свою персональную коллекцию городов'

        # Передаём TILE_LAYER для карты
        from django.conf import settings

        context['TILE_LAYER'] = getattr(
            settings, 'TILE_LAYER', 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        )

        return context


class PersonalCollectionList(ListView):  # type: ignore[type-arg]
    """
    Отображает список городов в персональной коллекции.
    """

    model = PersonalCollection
    paginate_by = 16

    def __init__(self) -> None:
        super().__init__()

        self.pk: uuid.UUID | None = None
        self.filter: str = ''
        self.cities: Any = None
        self.qty_of_cities: int | None = None
        self.qty_of_visited_cities: int | None = None
        self.collection: PersonalCollection | None = None

    def get(self, *args: Any, **kwargs: Any) -> Any:
        self.pk = self.kwargs['pk']

        # При обращении к несуществующей коллекции выдаём 404
        # Проверяем также, что коллекция принадлежит текущему пользователю или является публичной
        try:
            collection = PersonalCollection.objects.get(id=self.pk)
            # Коллекция доступна, если:
            # 1. Она публичная (is_public = True) - доступна всем, даже неавторизованным
            # 2. ИЛИ пользователь авторизован И является владельцем коллекции
            if not collection.is_public:
                if not self.request.user.is_authenticated or collection.user != self.request.user:
                    raise Http404
            # Сохраняем объект коллекции для использования в других методах
            self.collection = collection
        except ObjectDoesNotExist:
            logger.warning(
                self.request,
                f'(PersonalCollection #{self.pk}) Attempt to access a non-existent collection',
            )
            raise Http404

        return super().get(*args, **kwargs)

    def get_queryset(self) -> Any:
        """
        Получает из базы данных все города персональной коллекции.
        Города отображаются как посещённые/непосещённые на основе владельца коллекции.
        """
        if self.pk is None or self.collection is None:
            raise Http404

        # Используем владельца коллекции для определения посещённых городов
        self.cities = get_all_cities_from_personal_collection(
            self.pk,
            self.collection.user,
        )
        self.qty_of_visited_cities = sum([1 if city.is_visited else 0 for city in self.cities])
        self.qty_of_cities = len(self.cities)

        # Определяем фильтрацию
        filter_value = self.request.GET.get('filter')
        self.filter = filter_value if filter_value else ''
        if self.filter:
            try:
                self.cities = apply_filter_to_queryset(self.cities, self.filter)
            except KeyError:
                logger.warning(
                    self.request,
                    f'(PersonalCollection #{self.pk}) Unexpected value of the filter - {self.request.GET.get("filter")}',
                )
            else:
                logger.info(
                    self.request,
                    f"(PersonalCollection #{self.pk}) Using the filter '{self.filter}'",
                )

        return self.cities

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Для списка передаём упрощённые данные
        cities_data = [
            {
                'name': city.title,
                'lat': float(str(city.coordinate_width).replace(',', '.')),
                'lon': float(str(city.coordinate_longitude).replace(',', '.')),
                'is_visited': city.is_visited,
            }
            for city in self.cities
        ]
        context['cities'] = mark_safe(json.dumps(cities_data))

        context['filter'] = self.filter

        context['qty_of_cities'] = self.qty_of_cities
        context['qty_of_visited_cities'] = self.qty_of_visited_cities

        context['pk'] = self.pk
        if self.collection is not None:
            context['page_title'] = self.collection.title
            context['collection'] = self.collection
            context['page_description'] = (
                f'Города в персональной коллекции "{self.collection.title}".'
            )

        return context

    def get_template_names(self) -> list[str]:
        return [
            'collection/personal/list/page.html',
        ]


class PersonalCollectionMap(ListView):  # type: ignore[type-arg]
    """
    Отображает карту с городами персональной коллекции.
    """

    model = PersonalCollection
    paginate_by = 16

    def __init__(self) -> None:
        super().__init__()

        self.pk: uuid.UUID | None = None
        self.cities: Any = None
        self.qty_of_cities: int | None = None
        self.qty_of_visited_cities: int | None = None
        self.collection: PersonalCollection | None = None

    def get(self, *args: Any, **kwargs: Any) -> Any:
        self.pk = self.kwargs['pk']

        # При обращении к несуществующей коллекции выдаём 404
        # Проверяем также, что коллекция принадлежит текущему пользователю или является публичной
        try:
            collection = PersonalCollection.objects.get(id=self.pk)
            # Коллекция доступна, если:
            # 1. Она публичная (is_public = True) - доступна всем, даже неавторизованным
            # 2. ИЛИ пользователь авторизован И является владельцем коллекции
            if not collection.is_public:
                if not self.request.user.is_authenticated or collection.user != self.request.user:
                    raise Http404
            # Сохраняем объект коллекции для использования в других методах
            self.collection = collection
        except ObjectDoesNotExist:
            logger.warning(
                self.request,
                f'(PersonalCollection #{self.pk}) Attempt to access a non-existent collection',
            )
            raise Http404

        return super().get(*args, **kwargs)

    def get_queryset(self) -> Any:
        """
        Получает из базы данных все города персональной коллекции.
        Города отображаются как посещённые/непосещённые на основе владельца коллекции.
        """
        if self.pk is None or self.collection is None:
            raise Http404
        # Используем владельца коллекции для определения посещённых городов
        self.cities = get_all_cities_from_personal_collection(
            self.pk,
            self.collection.user,
        )
        self.qty_of_visited_cities = sum([1 if city.is_visited else 0 for city in self.cities])
        self.qty_of_cities = len(self.cities)

        return self.cities

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Для карты передаём полные данные о городах
        context['all_cities'] = self.cities

        context['qty_of_cities'] = self.qty_of_cities
        context['qty_of_visited_cities'] = self.qty_of_visited_cities

        # Передаём TILE_LAYER для карты
        from django.conf import settings

        context['TILE_LAYER'] = getattr(
            settings, 'TILE_LAYER', 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        )

        context['pk'] = self.pk
        if self.collection is not None:
            context['page_title'] = self.collection.title
            context['collection'] = self.collection
            context['page_description'] = (
                f'Карта городов в персональной коллекции "{self.collection.title}".'
            )

        return context

    def get_template_names(self) -> list[str]:
        return [
            'collection/personal/map/page.html',
        ]
