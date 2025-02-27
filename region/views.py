"""
Реализует классы для отображения списка регионов и городов конкретного региона.

* RegionList - Отображает список всех регионов с указанием количества городов в регионе.
* CitiesByRegionList - Отображает список всех городов в указанном регионе,
как посещённых, так и нет.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.http import Http404, HttpResponse
from django.views.generic import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.db.models import QuerySet

from MoiGoroda import settings
from region.models import Region
from city.models import VisitedCity, City
from services import logger
from services.db.regions_repo import (
    get_all_visited_regions,
    get_all_cities_in_region,
)
from services.db.selected_region.filter import apply_filter_to_queryset
from services.db.selected_region.sort import apply_sort_to_queryset
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
    Представление для вывода списка или карты городов в конкретном регионе.
    Поддерживает фильтрацию, сортировку и переключение между картой и списком.
    """

    model = VisitedCity
    paginate_by = 16

    sort: str = ''
    filter: str = ''
    region_id = None
    all_cities = None
    region_name = None
    list_or_map: str = ''
    total_qty_of_cities: int = 0
    qty_of_visited_cities: int = 0
    valid_filters = ('magnet', 'current_year', 'last_year')
    valid_sorts = ('name_down', 'name_up', 'date_down', 'date_up')

    def get(self, *args, **kwargs) -> HttpResponse:
        """
        Проверяет, существует ли указанный в URL регион в базе данных.
        В случае, если региона нет - возвращает ошибку 404.
        """
        self.region_id = self.kwargs['pk']

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
        Формирование списка городов в регионе.
        Фильтрует и сортирует данные в зависимости от параметров запроса.
        """
        self.filter = self.request.GET.get('filter')

        if self.request.user.is_authenticated:
            queryset = get_all_cities_in_region(self.request.user, self.region_id)
            queryset = self.apply_filter(queryset)
            queryset = queryset.values(
                'id',
                'title',
                'population',
                'date_of_foundation',
                'coordinate_width',
                'coordinate_longitude',
                'is_visited',
                'number_of_visits',
                'visited_id',
                'visit_dates',
                'first_visit_date',
                'last_visit_date',
                'has_magnet',
                'rating',
            )

            self.total_qty_of_cities = City.objects.filter(region_id=self.region_id).count()
            self.qty_of_visited_cities = queryset.filter(is_visited=True).count()
        else:
            queryset = City.objects.filter(region=self.region_id).values(
                'id',
                'title',
                'population',
                'date_of_foundation',
                'coordinate_width',
                'coordinate_longitude',
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

        # Для авторизованных пользователей определяем тип сортировки.
        # Сортировка для неавторизованного пользователя недоступна - она выставляется в значение `name_down`.
        queryset = self.apply_sort(queryset)

        return queryset

    def apply_filter(self, queryset: QuerySet[City]):
        """
        Применяет фильтр к набору данных, если параметр `filter` указан.
        """
        if self.filter:
            try:
                queryset = apply_filter_to_queryset(queryset, self.request.user, self.filter)
            except KeyError:
                logger.warning(
                    self.request, f"(Region) Unexpected value of the filter '{self.filter}'"
                )
        return queryset

    def apply_sort(self, queryset: QuerySet[City]):
        """
        Применяет сортировку к набору данных. Если параметр `sort` отсутствует,
        используется сортировка по умолчанию.
        """
        sort_default = 'default_auth' if self.request.user.is_authenticated else 'name_down'

        if self.request.user.is_authenticated:
            self.sort = self.request.GET.get('sort', sort_default)

            try:
                queryset = apply_sort_to_queryset(queryset, self.sort)
            except KeyError:
                logger.warning(
                    self.request, f"(Region) Unexpected value of the sorting '{self.sort}'"
                )
                queryset = apply_sort_to_queryset(queryset, sort_default)
                self.sort = 'name_down'
            else:
                if self.sort != 'default_auth' and self.sort != 'name_down':
                    logger.info(self.request, f"(Region) Using the sorting '{self.sort}'")

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Добавляет дополнительные параметры в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'sort': self.sort,
                'type': 'by_region',
                'filter': self.filter,
                'region_id': self.region_id,
                'all_cities': self.all_cities,
                'region_name': self.region_name,
                'iso3166_code': self.region_name.iso3166,
                'url_geo_polygons': settings.URL_GEO_POLYGONS,
                'total_qty_of_cities': self.total_qty_of_cities,
                'qty_of_visited_cities': self.qty_of_visited_cities,
                'declension_of_visited_cities': self.declension_of_city(self.qty_of_visited_cities),
                'declension_of_visited': self.declension_of_visited(self.qty_of_visited_cities),
                'url_for_filter_has_no_magnet': self.get_url_params(
                    'has_no_magnet' if self.filter != 'has_no_magnet' else '', self.sort
                ),
                'url_for_filter_has_magnet': self.get_url_params(
                    'has_magnet' if self.filter != 'has_magnet' else '', self.sort
                ),
                'url_for_filter_current_year': self.get_url_params(
                    'current_year' if self.filter != 'current_year' else '', self.sort
                ),
                'url_for_filter_last_year': self.get_url_params(
                    'last_year' if self.filter != 'last_year' else '', self.sort
                ),
                'url_for_sort_name_down': self.get_url_params(
                    self.filter, 'name_down' if self.sort != 'name_down' else ''
                ),
                'url_for_sort_name_up': self.get_url_params(
                    self.filter, 'name_up' if self.sort != 'name_up' else ''
                ),
                'url_for_sort_date_down': self.get_url_params(
                    self.filter,
                    'first_visit_date_down' if self.sort != 'first_visit_date_down' else '',
                ),
                'url_for_sort_date_up': self.get_url_params(
                    self.filter, 'first_visit_date_up' if self.sort != 'first_visit_date_up' else ''
                ),
                'url_for_sort_last_visit_date_down': self.get_url_params(
                    self.filter,
                    'last_visit_date_down' if self.sort != 'last_visit_date_down' else '',
                ),
                'url_for_sort_last_visit_date_up': self.get_url_params(
                    self.filter, 'last_visit_date_up' if self.sort != 'last_visit_date_up' else ''
                ),
            }
        )

        # Настройка заголовков страницы в зависимости от типа отображения
        page_type = 'Список городов' if self.list_or_map == 'list' else 'Города на карте'
        context.update(
            {
                'page_title': f'{self.region_name} - {page_type} региона',
                'page_description': f"{page_type} региона '{self.region_name}'",
            }
        )

        return context

    def get_template_names(self) -> list[str]:
        """
        Определяет шаблон в зависимости от режима отображения (список или карта).
        """
        template_name = (
            'region/region_selected__map.html'
            if self.list_or_map == 'map'
            else 'region/region_selected__list.html'
        )
        return [template_name]
