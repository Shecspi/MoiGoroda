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
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet, Subquery, IntegerField, OuterRef, Count

from MoiGoroda import settings
from country.models import Country
from region.models import Region
from city.models import VisitedCity, City
from services import logger
from region.services.db import (
    get_all_region_with_visited_cities,
    get_all_cities_in_region,
    get_all_regions,
)
from region.services.filter import apply_filter_to_queryset
from region.services.sort import apply_sort_to_queryset
from services.morphology import to_genitive
from utils.RegionListMixin import RegionListMixin


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
    country: str = ''
    country_code: str = ''
    country_id: str | None = None

    def __init__(self, list_or_map: str):
        super().__init__()

        self.list_or_map = list_or_map
        self.qty_of_regions: int = 0
        self.qty_of_visited_regions: int = 0

    def dispatch(self, request, *args, **kwargs):
        self.country_code = self.request.GET.get('country')
        if not self.country_code:
            if self.list_or_map == 'map':
                return redirect(reverse('region-all-map') + '?country=RU')
            else:
                return redirect(reverse('region-all-list') + '?country=RU')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Достаёт из базы данных все регионы, добавляя дополнительные поля:
        Достаёт из базы данных все регионы, добавляя дополнительные поля:
            * num_total - общее количество городов в регионе
            * num_visited - количество посещённых пользователем городов в регионе (для авторизованных пользователей)
        """
        try:
            country = Country.objects.get(code=self.country_code)
        except (Country.DoesNotExist, ValueError):
            raise Http404
        else:
            self.country = str(country)

        self.qty_of_regions = Region.objects.filter(country=country.id).count()

        if self.request.user.is_authenticated:
            queryset = get_all_region_with_visited_cities(self.request.user.pk, country.id)
            self.qty_of_visited_regions = queryset.filter(num_visited__gt=0).count()
        else:
            queryset = get_all_regions(country.id)

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

        context['country_id'] = self.country_id
        context['country_name'] = self.country
        context['country_code'] = self.country_code

        if self.list_or_map == 'list':
            context['page_title'] = (
                'Список регионов ' + f'{to_genitive(self.country).title()}'
                if self.country
                else '(все страны)'
            )
            context['page_description'] = (
                f'Список регионов {to_genitive(self.country).title()} с возможностью просмотра на карте. Актуальная информация об административном делении и расположении регионов.'
            )
        else:
            context['page_title'] = (
                'Карта регионов ' + f'{to_genitive(self.country).title()}'
                if self.country
                else '(все страны)'
            )
            context['page_description'] = (
                f'Карта регионов {to_genitive(self.country).title()}. Актуальная информация об административном делении и расположении регионов.'
            )

        return context

    def get_template_names(self) -> list[str]:
        if self.list_or_map == 'map':
            return [
                'region/region_all__map.html',
            ]
        else:
            return [
                'region/region_all__list.html',
            ]


class CitiesByRegionList(ListView):
    """
    Представление для вывода списка или карты городов в конкретном регионе.
    Поддерживает фильтрацию, сортировку и переключение между картой и списком.

    Допустимые параметры фильтрации указываются в region.services.filter.FILTER_FUNCTIONS.
    Если в URL передан недопустимый параметр, то self.filter будет иметь значение None.
    На это можно ориентироваться в шаблонах, есть ли сейчас активная фильтрация или нет.

    Допустимые параметры сортировки указываются в region.services.sort.SORT_FUNCTIONS.
    Если в URL не передан параметр sort или он имеет недопустимое значение, то будет использоваться сортировка по умолчанию - name_up.
    На это можно ориентироваться в шаблонах, есть ли сейчас активная фильтрация или нет.
    """

    model = VisitedCity

    sort: str = ''
    filter: str | None = None
    country_name: str = ''
    region_id = None
    region_name = None
    region_iso3166: str = ''
    all_cities = None
    list_or_map: str = ''
    number_of_cities: int = 0
    number_of_visited_cities: int = 0
    valid_filters = ('magnet', 'current_year', 'last_year')
    valid_sorts = ('name_down', 'name_up', 'date_down', 'date_up')

    def get(self, *args, **kwargs) -> HttpResponse:
        """
        Проверяет, существует ли указанный в URL регион в базе данных.
        В случае, если региона нет - возвращает ошибку 404.
        """
        self.region_id = self.kwargs['pk']

        try:
            region = Region.objects.get(id=self.region_id)
        except ObjectDoesNotExist as exc:
            logger.warning(
                self.request, f'(Region) Attempt to access a non-existent region #{self.region_id}'
            )
            raise Http404 from exc

        self.region_name = str(region)
        self.region_iso3166 = str(region.iso3166)
        self.country_name = str(region.country)

        return super().get(*args, **kwargs)

    def get_queryset(self) -> QuerySet[dict]:
        """
        Формирование списка городов в регионе.
        Фильтрует и сортирует данные в зависимости от параметров запроса.
        """
        self.filter = self.request.GET.get('filter') or None
        self.sort = self.request.GET.get('sort', None)

        if self.request.user.is_authenticated:
            queryset = get_all_cities_in_region(self.request.user, self.region_id)

            # Количество городов считаем до фильтрации, чтобы всегда было указано, сколько городов посещено
            self.number_of_cities = City.objects.filter(region_id=self.region_id).count()
            self.number_of_visited_cities = queryset.filter(is_visited=True).count()

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
                'number_of_users_who_visit_city',
                'number_of_visits_all_users',
            )
        else:
            # Подзапрос для получения количество пользователей, посетивших город
            number_of_users_who_visit_city = (
                VisitedCity.objects.filter(city=OuterRef('pk'), is_first_visit=True)
                .values('city')
                .annotate(count=Count('*'))
                .values('count')[:1]
            )

            # Подзапрос для получения общего количества посещений города
            number_of_visits_all_users = (
                VisitedCity.objects.filter(city=OuterRef('pk'))
                .values('city')
                .annotate(count=Count('*'))
                .values('count')[:1]
            )

            queryset = (
                City.objects.filter(region=self.region_id)
                .annotate(
                    number_of_users_who_visit_city=Subquery(
                        number_of_users_who_visit_city, output_field=IntegerField()
                    ),
                    number_of_visits_all_users=Subquery(number_of_visits_all_users),
                )
                .values(
                    'id',
                    'title',
                    'population',
                    'date_of_foundation',
                    'coordinate_width',
                    'coordinate_longitude',
                    'number_of_users_who_visit_city',
                    'number_of_visits_all_users',
                )
            )
            self.number_of_cities = queryset.count()

        if self.number_of_cities == 0:
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
                self.filter = None
                logger.warning(
                    self.request, f"(Region) Unexpected value of the filter '{self.filter}'"
                )
        return queryset

    def apply_sort(self, queryset: QuerySet[City]):
        """
        Применяет сортировку к набору данных. Если параметр `sort` отсутствует,
        используется сортировка по умолчанию.
        """
        sort_default = 'last_visit_date_down'

        try:
            queryset = apply_sort_to_queryset(
                queryset, self.sort, self.request.user.is_authenticated
            )
        except KeyError:
            logger.warning(self.request, f"(Region) Unexpected value of the sorting '{self.sort}'")
            queryset = apply_sort_to_queryset(
                queryset, sort_default, self.request.user.is_authenticated
            )
            self.sort = sort_default
        else:
            if self.sort is not None and self.sort != sort_default:
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
                'all_cities': self.all_cities,
                'country_name': self.country_name,
                'region_id': self.region_id,
                'region_name': self.region_name,
                'iso3166_code': self.region_iso3166,
                'url_geo_polygons': settings.URL_GEO_POLYGONS,
                'number_of_cities': self.number_of_cities,
                'number_of_visited_cities': self.number_of_visited_cities,
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


@xframe_options_exempt
def embedded_map(request, iso3166):
    return render(request, 'region/embedded_map.html', context={'iso3166': iso3166})
