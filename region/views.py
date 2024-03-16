"""
Реализует классы для отображения списка регионов и городов конкретного региона.

* RegionList - Отображает список всех регионов с указанием количества городов в регионе.
* CitiesByRegionList - Отображает список всех городов в указанном регионе,
как посещённых, так и нет.

----------------------------------------------

Copyright 2023 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime

from django.http import Http404
from django.views.generic import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Exists, OuterRef, Subquery, Value
from django.db.models import QuerySet, BooleanField, DateField, IntegerField

from region.models import Region
from city.models import VisitedCity, City
from services import logger
from services.db.visited_regions import get_all_visited_regions
from utils.RegionListMixin import RegionListMixin
from utils.CitiesByRegionMixin import CitiesByRegionMixin


class RegionList(RegionListMixin, ListView):
    """
    Отображает список всех регионов с указанием количества городов в регионе.
    Для авторизованных пользователей также указывается количество посещённых городов с прогресс-баром.

    Список разбивается на страницы, но на карте отображаются все регионы, вне зависимости от текущей страницы.

    Имеется возможность поиска региона по названию,
    в таком случае на карте будут отображены только найденные регионы.
    """

    model = Region
    paginate_by = 16
    all_regions = []
    list_or_map: str = ''

    def __init__(self, list_or_map: str):
        super().__init__()

        self.list_or_map = list_or_map
        self.qty_of_regions: int = 0
        self.qty_of_visited_regions: int = 0

    def get_queryset(self):
        """
        Достаёт из базы данных все регионы, добавляя дополнительные поля:
            * num_total - общее количество городов в регионе
            * num_visited - количество посещённых пользователем городов в регионе
        """
        self.qty_of_regions = Region.objects.count()

        if self.request.user.is_authenticated:
            queryset = get_all_visited_regions(self.request.user.pk)
            self.qty_of_visited_regions = queryset.filter(num_visited__gt=0).count()
        else:
            queryset = (
                Region.objects.select_related('area')
                .annotate(num_total=Count('city', distinct=True))
                .order_by('title')
            )

        if self.list_or_map == 'list':
            logger.info(self.request, '(Region) Viewing the list of regions')
        else:
            logger.info(self.request, '(Region) Viewing the map of regions')

        if self.request.GET.get('filter'):
            f = self.request.GET.get('filter')
            logger.info(self.request, f"(Region) Using the filter '{f}'")
            queryset = queryset.filter(title__contains=f.capitalize())

        # Эта дополнительная переменная используется для отображения регионов на карте.
        # Она нужна, так как queryset на этапе обработки пагинации
        # режет запрос по количеству записей на странице.
        # И если для карты использовать queryset (object_list),
        # то отобразится только paginate_by регионов, а нужно все.
        self.all_regions = queryset

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_page'] = 'region_list' if self.list_or_map == 'list' else 'region_map'
        context['all_regions'] = self.all_regions
        context['qty_of_regions'] = self.qty_of_regions
        context['qty_of_visited_regions'] = self.qty_of_visited_regions
        context['declension_of_regions'] = self.declension_of_region(self.qty_of_visited_regions)
        context['declension_of_visited'] = self.declension_of_visited(self.qty_of_visited_regions)

        if self.list_or_map == 'list':
            context['page_title'] = 'Список регионов России'
            context['page_description'] = 'Список регионов России'
        else:
            context['page_title'] = 'Карта регионов России'
            context['page_description'] = 'Карта с отмеченными регионами России'

        return context

    def get_template_names(self) -> list[str]:
        if self.list_or_map == 'list':
            return [
                'region/region_all__list.html',
            ]
        elif self.list_or_map == 'map':
            return [
                'region/region_all__map.html',
            ]


class CitiesByRegionList(ListView, CitiesByRegionMixin):
    """
    Отображает список всех городов в указанном регионе, как посещённых, так и нет.

    Фильтрация городов передаётся через GET-параметр `filter` и может принимать одно из следующих значений:
        * `magnet` - наличие магнита
        * `current_year` - посещённые в текущем году
        * `last_yesr` - посещённые в прошлом году

    Фильтрация городов передаётся через GET-параметр `sort` и может принимать одно из следующих значений:
        * `name_down` - по возрастанию имени
        * `name_up` - по убыванию имени
        * `date_down` - по возрастанию даты посещений
        * `date_up` - по убыванию даты посещения
    """

    model = VisitedCity
    paginate_by = 16
    list_or_map: str = ''

    all_cities = None
    region_id = None
    region_name = None

    filter = None
    sort = None

    valid_filters = ('magnet', 'current_year', 'last_year')
    valid_sorts = ('name_down', 'name_up', 'date_down', 'date_up')

    def __init__(self, list_or_map: str):
        super().__init__()

        self.sort: str = ''
        self.filter: str = ''
        self.total_qty_of_cities: int = 0
        self.qty_of_visited_cities: int = 0
        self.qty_of_visited_cities_current_year: int = 0

        self.list_or_map = list_or_map

    def get(self, *args, **kwargs):
        """
        Проверяет, существует ли указанный в URL регион в базе данных.
        В случае, если региона нет - возвращает ошибку 404.
        """
        # Проверка этого параметра не нужна, так как это реализовано на уровне Django
        self.region_id = self.kwargs['pk']

        # При обращении к несуществующему региону выдаём 404
        # При этом в указанном регионе может не быть посещённых городов, это ок
        try:
            self.region_name = Region.objects.get(id=self.region_id)
        except ObjectDoesNotExist as exc:
            logger.warning(
                self.request, f'(Region) Attempt to access a non-existent region #{self.region_id}'
            )
            raise Http404 from exc

        return super().get(*args, **kwargs)

    def get_queryset(self) -> QuerySet[dict]:
        """
        Получает из базы данных все города в указанном регионе, как посещённые, так и нет.
        Возвращает Queryset, состоящий из полей:
            * `id` - ID города
            * `title` - название города
            * `population` - население города
            * `date_of_foundation` - дата основания города
            * `coordinate_width` - широта
            * `coordinate_longitude` - долгота
            * `is_visited` - True,если город посещён
            * `date_of_visit` - дата посещения

            Для авторизованных пользователей доступны дополнительные поля:
            * `visited_id` - ID посещённого города
            * `has_magnet` - True, если имеется магнит
            * `rating` - рейтинг от 1 до 5
        """
        if self.request.user.is_authenticated:
            queryset = (
                City.objects.filter(region=self.region_id)
                .annotate(
                    is_visited=Exists(
                        VisitedCity.objects.filter(city_id=OuterRef('pk'), user=self.request.user)
                    ),
                    visited_id=Subquery(
                        VisitedCity.objects.filter(
                            city_id=OuterRef('pk'), user=self.request.user
                        ).values('id'),
                        output_field=IntegerField(),
                    ),
                    date_of_visit=Subquery(
                        VisitedCity.objects.filter(
                            city_id=OuterRef('pk'), user=self.request.user
                        ).values('date_of_visit'),
                        output_field=DateField(),
                    ),
                    has_magnet=Subquery(
                        VisitedCity.objects.filter(
                            city_id=OuterRef('pk'), user=self.request.user
                        ).values('has_magnet'),
                        output_field=BooleanField(),
                    ),
                    rating=Subquery(
                        VisitedCity.objects.filter(
                            city_id=OuterRef('pk'), user=self.request.user
                        ).values('rating'),
                        output_field=IntegerField(),
                    ),
                )
                .values(
                    'id',
                    'title',
                    'population',
                    'date_of_foundation',
                    'coordinate_width',
                    'coordinate_longitude',
                    'is_visited',
                    'visited_id',
                    'date_of_visit',
                    'has_magnet',
                    'rating',
                )
            )
            self.total_qty_of_cities = queryset.count()
            self.qty_of_visited_cities = queryset.filter(is_visited=True).count()
            self.qty_of_visited_cities_current_year = queryset.filter(
                is_visited=True, date_of_visit__year=datetime.now().year
            ).count()
        else:
            # Если пользователь не авторизован, то поля `is_visited` и `date_of_visit` всё-равно нужны.
            # `is_visited` для шаблона, чтобы он отображал все города как непосещённые.
            # `date_of_visit` для сортировки. В данном случае сортировка по этому полю не принесёт никакого эффекта,
            # но в коде это заложено, поэтому поле нужно.
            queryset = (
                City.objects.filter(region=self.region_id)
                .annotate(is_visited=Value(False), date_of_visit=Value(0))
                .values(
                    'id',
                    'title',
                    'population',
                    'date_of_foundation',
                    'coordinate_width',
                    'coordinate_longitude',
                    'is_visited',
                )
            )
            self.total_qty_of_cities = queryset.count()

        if self.total_qty_of_cities == 0:
            logger.warning(
                self.request, f'(Region) There is no cities in the region #{self.region_id}'
            )

        if self.list_or_map == 'list':
            logger.info(
                self.request, f'(Region) Viewing the list of cities in the region #{self.region_id}'
            )
        else:
            logger.info(
                self.request, f'(Region) Viewing the map of cities in the region #{self.region_id}'
            )

        # Дополнительная переменная нужна, так как используется пагинация и Django на уровне SQL-запроса
        # устанавливает лимит на выборку, равный `paginate_by`.
        # Из-за этого на карте отображается только `paginate_by` городов.
        # Чтобы отображались все города - используем доп. переменную без лимита.
        self.all_cities = queryset

        # Определяем фильтрацию
        if self.request.user.is_authenticated:
            self.filter = self.request.GET.get('filter') if self.request.GET.get('filter') else ''
            if self.filter:
                try:
                    queryset = self.apply_filter_to_queryset(queryset, self.filter)
                except KeyError:
                    logger.warning(
                        self.request, f"(Region) Unexpected value of the filter '{self.filter}'"
                    )
                else:
                    logger.info(self.request, f"(Region) Using the filter '{self.filter}'")

        # Для авторизованных пользователей определяем тип сортировки.
        # Сортировка для неавторизованного пользователя недоступна - она выставляется в значение `default_guest`.
        sort_default = 'default_auth' if self.request.user.is_authenticated else 'default_guest'
        if self.request.user.is_authenticated:
            self.sort = (
                self.request.GET.get('sort') if self.request.GET.get('sort') else sort_default
            )
            try:
                queryset = self.apply_sort_to_queryset(queryset, self.sort)
            except KeyError:
                logger.warning(
                    self.request, f"(Region) Unexpected value of the sorting '{self.filter}'"
                )
                queryset = self.apply_sort_to_queryset(queryset, sort_default)
                self.sort = ''
            else:
                if self.sort != 'default_auth' and self.sort != 'default_guest':
                    logger.info(self.request, f"(Region) Using the sorting '{self.sort}'")

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sort'] = self.sort
        context['type'] = 'by_region'
        context['filter'] = self.filter
        context['region_id'] = self.region_id
        context['all_cities'] = self.all_cities
        context['region_name'] = self.region_name

        context['total_qty_of_cities'] = self.total_qty_of_cities
        context['qty_of_visited_cities'] = self.qty_of_visited_cities
        context['qty_of_visited_cities_current_year'] = self.qty_of_visited_cities_current_year
        context['declension_of_visited_cities'] = self.declension_of_city(
            self.qty_of_visited_cities
        )
        context['declension_of_visited'] = self.declension_of_visited(self.qty_of_visited_cities)

        context['url_for_filter_magnet'] = self.get_url_params(
            'magnet' if self.filter != 'magnet' else '', self.sort
        )
        context['url_for_filter_current_year'] = self.get_url_params(
            'current_year' if self.filter != 'current_year' else '', self.sort
        )
        context['url_for_filter_last_year'] = self.get_url_params(
            'last_year' if self.filter != 'last_year' else '', self.sort
        )
        context['url_for_sort_name_down'] = self.get_url_params(self.filter, 'name_down')
        context['url_for_sort_name_up'] = self.get_url_params(self.filter, 'name_up')
        context['url_for_sort_date_down'] = self.get_url_params(self.filter, 'date_down')
        context['url_for_sort_date_up'] = self.get_url_params(self.filter, 'date_up')

        if self.list_or_map == 'list':
            context['page_title'] = self.region_name
            context['page_description'] = f"Список городов региона '{self.region_name}'"
        else:
            context['page_title'] = self.region_name
            context['page_description'] = (
                f"Карта с отмеченными городами региона '{self.region_name}'"
            )

        return context

    def get_template_names(self) -> list[str]:
        if self.list_or_map == 'list':
            return [
                'region/region_selected__list.html',
            ]
        elif self.list_or_map == 'map':
            return [
                'region/region_selected__map.html',
            ]
