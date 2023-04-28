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
import logging

from django.http import Http404
from django.views.generic import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count, Exists, OuterRef, Subquery, Value
from django.db.models import QuerySet, BooleanField, DateField, IntegerField

from region.models import Region
from city.models import VisitedCity, City
from utils.sort_funcs import sort_validation, apply_sort
from utils.filter_funcs import filter_validation, apply_filter


logger = logging.getLogger('moi-goroda')


class RegionList(ListView):
    """
    Отображает список всех регионов с указанием количества городов в регионе.
    Для авторизованных пользователей также указывается количество посещённых городов с прогресс-баром.

    Список разбивается на страницы, но на карте отображаются все регионы, вне зависимости от текущей страницы.

    Имеется возможность поиска региона по названию,
    в таком случае на карте будут отображены только найденные регионы.
    """
    model = Region
    paginate_by = 16
    template_name = 'region/region__list.html'
    all_regions = []

    def get_queryset(self):
        """
        Достаёт из базы данных все регионы, добавляя дополнительные поля:
            * num_total - общее количество городов в регионе
            * num_visited - количество посещённых пользователем городов в регионе
        """
        if self.request.user.is_authenticated:
            queryset = Region.objects.select_related('area').annotate(
                num_total=Count('city', distinct=True),
                num_visited=Count(
                    'city',
                    filter=Q(city__visitedcity__user=self.request.user.pk),
                    distinct=True
                )
            ).order_by('-num_visited', 'title')
        else:
            logger.info(f'Viewing the page by not authorized user: {self.request.get_full_path()}')
            queryset = Region.objects.select_related('area').annotate(
                num_total=Count('city', distinct=True)
            ).order_by('title')

        if self.request.GET.get('filter'):
            logger.info(f'Using a filter to search for a region: {self.request.get_full_path()}')
            queryset = queryset.filter(title__contains=self.request.GET.get('filter').capitalize())

        # Эта дополнительная переменная используется для отображения регионов на карте.
        # Она нужна, так как queryset на этапе обработки пагинации
        # режет запрос по количеству записей на странице.
        # И если для карты использовать queryset (object_list),
        # то отобразится только paginate_by регионов, а нужно все.
        self.all_regions = queryset

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['all_regions'] = self.all_regions

        return context


class CitiesByRegionList(ListView):
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
    template_name = 'region/cities_by_region__list.html'

    all_cities = None
    region_id = None
    region_name = None

    filter = None
    sort = None

    valid_filters = ('magnet', 'current_year', 'last_year')
    valid_sorts = ('name_down', 'name_up', 'date_down', 'date_up')

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
            logger.warning(f'Attempt to access a non-existent region: {self.request.get_full_path()}')
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
            queryset = City.objects.filter(region=self.region_id).annotate(
                is_visited=Exists(
                    VisitedCity.objects.filter(city_id=OuterRef('pk'), user=self.request.user)
                ),
                visited_id=Subquery(
                    VisitedCity.objects.filter(city_id=OuterRef('pk'), user=self.request.user).values('id'),
                    output_field=IntegerField()
                ),
                date_of_visit=Subquery(
                    VisitedCity.objects.filter(city_id=OuterRef('pk'), user=self.request.user).values('date_of_visit'),
                    output_field=DateField()
                ),
                has_magnet=Subquery(
                    VisitedCity.objects.filter(city_id=OuterRef('pk'), user=self.request.user).values('has_magnet'),
                    output_field=BooleanField()
                ),
                rating=Subquery(
                    VisitedCity.objects.filter(city_id=OuterRef('pk'), user=self.request.user).values('rating'),
                    output_field=IntegerField()
                )
            ).values(
                'id', 'title', 'population', 'date_of_foundation',
                'coordinate_width', 'coordinate_longitude',
                'is_visited', 'visited_id', 'date_of_visit', 'has_magnet', 'rating'
            )
        else:
            # Если пользователь не авторизован, то поля `is_visited` и `date_of_visit` всё-равно нужны.
            # `is_visited` для шаблона, чтобы он отображал все города как непосещённые.
            # `date_of_visit` для сортировки. В данном случае сортировка по этому полю не принесёт никакого эффекта,
            # но в коде это заложено, поэтому поле нужно.
            logger.info(f'Viewing the page by not authorized user: {self.request.get_full_path()}')
            queryset = City.objects.filter(region=self.region_id).annotate(
                is_visited=Value(False),
                date_of_visit=Value(0)
            ).values(
                'id', 'title', 'population', 'date_of_foundation',
                'coordinate_width', 'coordinate_longitude', 'is_visited'
            )

        # Дополнительная переменная нужна, так как используется пагинация и Django на уровне SQL-запроса
        # устанавливает лимит на выборку, равный `paginate_by`.
        # Из-за этого на карте отображается только `paginate_by` городов.
        # Чтобы отображались все города - используем доп. переменную без лимита.
        self.all_cities = queryset

        sort_value = ''
        if self.request.user.is_authenticated:
            if self.request.GET.get('filter'):
                filter_value = self.request.GET.get('filter')
                self.filter = filter_validation(filter_value, self.valid_filters)
                if self.filter:
                    logger.info(f'Using a filter for cities: {self.request.get_full_path()}')
                    queryset = apply_filter(queryset, filter_value)
                else:
                    logger.warning(f'Attempt to access a non-existent filter: {self.request.get_full_path()}')
            if self.request.GET.get('sort'):
                sort_value = self.request.GET.get('sort')
                self.sort = sort_validation(sort_value, self.valid_sorts)
                if self.sort:
                    logger.info(f'Using a sort for cities: {self.request.get_full_path()}')
                else:
                    logger.warning(f'Attempt to access a non-existent sort: {self.request.get_full_path()}')
        # Сортировка нужна в любом случае, поэтому она не в блоке if
        queryset = apply_sort(queryset, sort_value)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sort'] = self.sort
        context['type'] = 'by_region'
        context['filter'] = self.filter
        context['region_id'] = self.region_id
        context['all_cities'] = self.all_cities
        context['region_name'] = self.region_name

        return context
