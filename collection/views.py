"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import json
import uuid
from typing import Any, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
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
from collection.repository import CollectionRepository
from collection.services import PersonalCollectionService, get_all_cities_from_collection
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
        Получает из базы данных все города коллекции.
        Города отображаются как посещённые/непосещённые на основе текущего пользователя.
        """
        if self.pk is None:
            raise Http404
        self.cities = get_all_cities_from_collection(
            self.pk,
            self.request.user if self.request.user.is_authenticated else None,
        )
        self.qty_of_visited_cities = sum([1 if city.is_visited else 0 for city in self.cities])
        self.qty_of_cities = len(self.cities)

        # Определяем фильтрацию
        filter_value = self.request.GET.get('filter')
        self.filter = filter_value if filter_value else ''
        if self.filter:
            try:
                self.cities = apply_filter_to_queryset(self.cities, self.filter)
                if self.list_or_map == 'list':
                    logger.info(
                        self.request,
                        f"(Collection #{self.pk}) Using the filter '{self.filter}'",
                    )
                else:
                    logger.info(
                        self.request,
                        f"(Collection #{self.pk}) Using the filter '{self.filter}'",
                    )
            except KeyError:
                logger.warning(
                    self.request,
                    f'(Collection #{self.pk}) Unexpected value of the filter - {self.request.GET.get("filter")}',
                )
            else:
                if self.filter:
                    if self.list_or_map == 'list':
                        logger.info(
                            self.request,
                            f"(Collection #{self.pk}) Using the filter '{self.filter}'",
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


class PersonalCollectionEdit(LoginRequiredMixin, TemplateView):
    """
    Отображает страницу редактирования персональной коллекции.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Только владелец коллекции может редактировать её.
     > Вся логика формы обрабатывается на фронтенде через JS.
    """

    template_name = 'collection/personal/create/page.html'

    def get(self, *args: Any, **kwargs: Any) -> Any:
        """
        Проверяет доступ к редактированию коллекции.
        """
        from collection.services import PersonalCollectionService

        service = PersonalCollectionService()
        self.collection = service.get_collection_with_access_check(
            self.kwargs['pk'], self.request.user
        )

        # Проверяем, что пользователь является владельцем коллекции
        if self.collection.user != self.request.user:
            raise Http404

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['active_page'] = 'collection'
        context['page_title'] = f'Редактирование коллекции "{self.collection.title}"'
        context['page_description'] = 'Измените данные вашей персональной коллекции'

        # Передаём коллекцию в контекст для тестов и шаблона
        context['collection'] = self.collection

        # Передаём данные коллекции для предзаполнения формы
        context['collection_id'] = str(self.collection.id)
        context['collection_title'] = self.collection.title
        context['collection_is_public'] = self.collection.is_public
        context['collection_city_ids'] = list(self.collection.city.values_list('id', flat=True))

        # Передаём TILE_LAYER для карты
        from django.conf import settings

        context['TILE_LAYER'] = getattr(
            settings, 'TILE_LAYER', 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        )

        return context


class PersonalCollectionListView(LoginRequiredMixin, ListView):  # type: ignore[type-arg]
    """
    View для отображения списка персональных коллекций пользователя.
    Отображает страницу со всеми персональными коллекциями пользователя.
    """

    model = PersonalCollection
    paginate_by = 16
    template_name = 'collection/personal/collections/page.html'

    def __init__(self) -> None:
        super().__init__()
        self.repository = CollectionRepository()

    def get_queryset(self) -> Any:
        """
        Получает QuerySet персональных коллекций пользователя.
        """
        # LoginRequiredMixin гарантирует, что self.request.user - это User, а не AnonymousUser
        user = cast(User, self.request.user)
        return self.repository.get_personal_collections_with_annotations(user)

    def get_context_data(self, *, object_list: Any = None, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)

        # Получаем список ID городов, которые посещены пользователем
        user = cast(User, self.request.user)
        context['visited_cities'] = list(
            VisitedCity.objects.filter(user=user).values_list('city__id', flat=True)
        )

        context['active_page'] = 'collection'
        context['page_title'] = 'Персональные коллекции'
        context['page_description'] = (
            'Ваши персональные коллекции городов. Создавайте свои коллекции и делитесь ими с другими.'
        )

        return context


class PublicPersonalCollectionListView(ListView):  # type: ignore[type-arg]
    """
    View для отображения списка публичных персональных коллекций всех пользователей.
    Отображает страницу со всеми публичными персональными коллекциями в виде таблицы.
    """

    model = PersonalCollection
    paginate_by = 16
    template_name = 'collection/public/list/page.html'

    def __init__(self) -> None:
        super().__init__()
        self.repository = CollectionRepository()

    def get_queryset(self) -> Any:
        """
        Получает QuerySet публичных персональных коллекций.
        """
        return self.repository.get_public_collections_with_annotations()

    def get_context_data(self, *, object_list: Any = None, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)

        # Ограничиваем до 15 городов для каждой коллекции после prefetch
        # Prefetch загружает все города, но мы ограничиваем до первых 15 по алфавиту
        paginated_collections = context.get('object_list', [])
        for collection in paginated_collections:
            if hasattr(collection, 'first_15_cities'):
                collection.first_15_cities = collection.first_15_cities[:15]

        context['active_page'] = 'collection'
        context['page_title'] = 'Публичные персональные коллекции'
        context['page_description'] = (
            'Публичные персональные коллекции городов всех пользователей. Исследуйте коллекции других пользователей.'
        )

        return context


class PersonalCollectionCityListView(ListView):  # type: ignore[type-arg]
    """
    View для отображения списка городов в персональной коллекции.
    Отображает детальную страницу коллекции со списком городов.
    Слой API - только получение параметров из request и вызов сервиса.
    """

    model = PersonalCollection
    paginate_by = 16

    def __init__(self) -> None:
        super().__init__()
        self.service = PersonalCollectionService()
        self.pk: uuid.UUID | None = None
        self.collection: PersonalCollection | None = None

    def get(self, *args: Any, **kwargs: Any) -> Any:
        """
        Получает коллекцию с проверкой доступа через сервис.
        """
        self.pk = self.kwargs['pk']
        self.collection = self.service.get_collection_with_access_check(self.pk, self.request.user)
        return super().get(*args, **kwargs)

    def get_queryset(self) -> Any:
        """
        Получает QuerySet городов через сервис.
        """
        assert self.pk is not None and self.collection is not None

        filter_value = self.request.GET.get('filter')
        cities, statistics = self.service.get_cities_for_collection(
            self.pk, self.collection.user, filter_value
        )

        # Сохраняем статистику для использования в get_context_data
        self._statistics = statistics

        return cities

    def get_context_data(self, *, object_list: Any = None, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует контекст для шаблона через сервис.
        """
        assert self.collection is not None

        context = super().get_context_data(object_list=object_list, **kwargs)

        # Используем object_list из контекста (уже пагинированный)
        cities = context.get('object_list', [])

        service_context = self.service.get_list_context_data(
            collection=self.collection,
            cities=cities,
            filter_param=self._statistics.get('filter', ''),
            statistics=self._statistics,
        )

        # Обновляем контекст (service_context не содержит object_list, поэтому он не перезапишется)
        context.update(service_context)

        return context

    def get_template_names(self) -> list[str]:
        return [
            'collection/personal/cities/list/page.html',
        ]


class PersonalCollectionMap(ListView):  # type: ignore[type-arg]
    """
    View для отображения карты с городами персональной коллекции.
    Слой API - только получение параметров из request и вызов сервиса.
    """

    model = PersonalCollection

    def __init__(self) -> None:
        super().__init__()

        self.service = PersonalCollectionService()
        self.pk: uuid.UUID | None = None
        self.collection: PersonalCollection | None = None

    def get(self, *args: Any, **kwargs: Any) -> Any:
        """
        Получает коллекцию с проверкой доступа через сервис.
        """
        self.pk = self.kwargs['pk']
        self.collection = self.service.get_collection_with_access_check(self.pk, self.request.user)
        return super().get(*args, **kwargs)

    def get_queryset(self) -> Any:
        """
        Получает QuerySet городов через сервис.
        """
        assert self.pk is not None and self.collection is not None

        cities, statistics = self.service.get_cities_for_collection(
            self.pk, self.collection.user, None
        )

        # Сохраняем статистику для использования в get_context_data
        self._statistics = statistics

        return cities

    def get_context_data(self, *, object_list: Any = None, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует контекст для шаблона через сервис.
        """
        assert self.collection is not None

        context = super().get_context_data(object_list=object_list, **kwargs)

        # Используем object_list из контекста (уже пагинированный)
        cities = context.get('object_list', [])

        service_context = self.service.get_map_context_data(
            collection=self.collection,
            cities=cities,
        )

        context.update(service_context)

        return context

    def get_template_names(self) -> list[str]:
        return [
            'collection/personal/cities/map/page.html',
        ]
