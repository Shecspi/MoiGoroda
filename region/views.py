from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q, QuerySet
from django.http import Http404
from django.views.generic import ListView

from region.models import Region
from travel.models import VisitedCity, City
from travel.views import logger, prepare_log_string, _create_list_of_coordinates


class Region_List(LoginRequiredMixin, ListView):
    """
    Отображает список всех регионов с указанием количества посещённых городов в каждом.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """
    model = Region
    paginate_by = 16
    template_name = 'travel/region/list.html'
    all_regions = []

    def get_queryset(self):
        self.all_regions = Region.objects.select_related('area').annotate(
            num_visited=Count('city', filter=Q(city__visitedcity__user=self.request.user.pk), distinct=True)
        )
        queryset = (Region.objects
                    .select_related('area')
                    .annotate(
                        num_total=Count('city', distinct=True),
                        num_visited=Count(
                            'city',
                            filter=Q(city__visitedcity__user=self.request.user.pk),
                            distinct=True
                        )
                    ).order_by('-num_visited', 'title'))
        if self.request.GET.get('filter'):
            queryset = queryset.filter(title__contains=self.request.GET.get('filter').capitalize())

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['all_regions'] = self.all_regions
        context['breadcrumb'] = [
            {'url': 'main_page', 'title': 'Главная', 'active': False},
            {'url': '', 'title': 'Список регионов России', 'active': True}
        ]

        return context


class VisitedCity_List(LoginRequiredMixin, ListView):
    """
    Отображает список посещённых городов пользователя, а конкретно:
        * все посещённые города, если в URL-запросе не указан параметр 'pk'
        * посещённые города конкретного региона, если параметр 'pk' указан.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """
    model = VisitedCity
    paginate_by = 16
    template_name = 'travel/visited_city/list.html'

    # Список, хранящий координаты и название посещённого города.
    # В шаблоне используется для генерации отметок на карте.
    coords_of_visited_cities = []

    # Список, хранящий все города указанного в URL региона, за исключением посещённых пользователем.
    coords_of_not_visited_cities = []

    # ID и название региона, для которого необходимо показать посещённые города.
    # В случае отсутствия этого параметра - отобразится список всех посещённых городов.
    region_id = None
    region_name = None

    filter = None
    sort = None

    valid_filters = ['magnet', 'current_year', 'last_year']
    valid_sorts = ['name_down', 'name_up', 'date_down', 'date_up']

    def get(self, *args, **kwargs):
        if self.kwargs:
            self.region_id = self.kwargs['pk']

            # При обращении к несуществующему региону выдаём 404
            # При этом в указанном регионе может не быть посещённых городов, это ок
            try:
                Region.objects.get(id=self.region_id)
            except ObjectDoesNotExist:
                logger.warning(
                    prepare_log_string(404, 'Attempt to update a non-existent region.', self.request),
                    extra={'classname': self.__class__.__name__}
                )
                raise Http404

        return super().get(*args, **kwargs)

    def get_queryset(self) -> QuerySet[dict]:
        """
        Получает из базы данных либо все посещённые города пользователя,
        либо только из конкретного региона, указанного в параметре 'pk' в URL.

        Также генерирует список координат посещённых городов.
        Если указан 'pk', то дополнительно генерируется список координат непосещённых городов.
        """
        queryset = VisitedCity.objects \
            .filter(user=self.request.user) \
            .select_related('city', 'region') \
            .only('id', 'city__id', 'city__title', 'city__coordinate_width', 'city__coordinate_longitude',
                  'region__id', 'region__title', 'region__type', 'date_of_visit', 'has_magnet', 'rating')

        if self.request.GET.get('filter'):
            self.filter = self._check_validity_of_filter_value(self.request.GET.get('filter'))
            queryset = self._apply_filter_to_queryset(queryset)

        if self.request.GET.get('sort'):
            self.sort = self._check_validity_of_sort_value(self.request.GET.get('sort'))
        queryset = self._apply_sort_to_queryset(queryset)  # Сортировка нужна в любом случае, поэтому она не в блоке if

        # Если в URL указан ID региона, то отображаем только посещённые города в этом регионе.
        if self.region_id:
            queryset = queryset.filter(region_id=self.region_id)
            self.region_name = Region.objects.get(id=self.region_id)
            self.coords_of_visited_cities = _create_list_of_coordinates(queryset)
            self.coords_of_not_visited_cities = []
            queryset_all_cities = City.objects \
                .filter(region_id=self.region_id) \
                .only('title', 'coordinate_width', 'coordinate_longitude')

            for city in queryset_all_cities:
                tmp = [city.coordinate_width,
                       city.coordinate_longitude,
                       city.title]
                if tmp not in self.coords_of_visited_cities:
                    self.coords_of_not_visited_cities.append(tmp)
        else:
            # Список с координатами посещённых городов
            self.coords_of_visited_cities = _create_list_of_coordinates(queryset)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['coords_of_visited_cities'] = self.coords_of_visited_cities
        context['filter'] = self.filter
        context['sort'] = self.sort

        if self.region_id:
            context['type'] = 'by_region'
            context['region_id'] = self.region_id
            context['coords_of_not_visited_cities'] = self.coords_of_not_visited_cities
            context['region_name'] = self.region_name
            context['breadcrumb'] = [
                {'url': 'main_page', 'title': 'Главная', 'active': False},
                {'url': 'city-all', 'title': 'Список посещённых городов', 'active': False},
                {'url': '', 'title': self.region_name, 'active': True},
            ]
        else:
            context['type'] = 'all'
            context['breadcrumb'] = [
                {'url': 'main_page', 'title': 'Главная', 'active': False},
                {'url': '', 'title': 'Список посещённых городов', 'active': True}
            ]

        return context

    def _check_validity_of_filter_value(self, filter_value: str) -> str | None:
        if filter_value in self.valid_filters:
            return filter_value
        else:
            return None

    def _check_validity_of_sort_value(self, sort_value: str) -> str | None:
        if sort_value in self.valid_sorts:
            return sort_value
        else:
            return None

    def _apply_filter_to_queryset(self, queryset: QuerySet) -> QuerySet:
        match self.filter:
            case 'magnet':
                queryset = queryset.filter(has_magnet=False)
            case 'current_year':
                queryset = queryset.filter(date_of_visit__year=datetime.now().year)
            case 'last_year':
                queryset = queryset.filter(date_of_visit__year=datetime.now().year - 1)

        return queryset

    def _apply_sort_to_queryset(self, queryset: QuerySet) -> QuerySet:
        match self.sort:
            case 'name_down':
                queryset = queryset.order_by('city__title')
            case 'name_up':
                queryset = queryset.order_by('-city__title')
            case 'date_down':
                queryset = queryset.order_by('date_of_visit')
            case 'date_up':
                queryset = queryset.order_by('-date_of_visit')
            case _:
                queryset = queryset.order_by('-date_of_visit', 'city__title')

        return queryset

