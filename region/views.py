from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q, QuerySet
from django.http import Http404
from django.views.generic import ListView

from region.models import Region
from city.models import VisitedCity, City
from city.views import logger, prepare_log_string, _create_list_of_coordinates
from utils.VisitedCityMixin import VisitedCityMixin


class Region_List(LoginRequiredMixin, ListView):
    """
    Отображает список всех регионов с указанием количества посещённых городов в каждом.
    Список разбивается на страницы, но на карте отображаются все регионы,
    вне зависимости от текущей страницы.
    Имеется возможность поиска региона по названию,
    в таком случае на карте будут отображены только найденные регионы.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
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
        queryset = (Region.objects
                    .select_related('area')
                    .annotate(num_total=Count('city', distinct=True),
                              num_visited=Count('city',
                                                filter=Q(city__visitedcity__user=self.request.user.pk),
                                                distinct=True))
                    .order_by('-num_visited', 'title'))
        if self.request.GET.get('filter'):
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


class CitiesByRegion_List(VisitedCityMixin, LoginRequiredMixin, ListView):
    """
    Отображает список посещённых городов пользователя в указанном регионе.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """
    model = VisitedCity
    paginate_by = 16
    template_name = 'region/cities_by_region__list.html'

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
        """
        Проверяет, существует ли указанный в URL регион в базе данных.
        В случае, если региона нет - возвращает ошибку 404.
        """
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
        Получает из базы данных все посещённые города пользователя в указанном регионе.

        Также генерирует списки координат посещённых и непосещённых городов.
        """
        queryset = (
            VisitedCity.objects
            .filter(user=self.request.user)
            .select_related('city', 'region')
            .only('id', 'date_of_visit', 'has_magnet', 'rating',
                  'city__id', 'city__title', 'city__coordinate_width', 'city__coordinate_longitude',
                  'region__id', 'region__title', 'region__type')
            .filter(region_id=self.region_id)
        )

        if self.request.GET.get('filter'):
            self.filter = self._check_validity_of_filter_value(self.request.GET.get('filter'))
            queryset = self._apply_filter_to_queryset(queryset)

        if self.request.GET.get('sort'):
            self.sort = self._check_validity_of_sort_value(self.request.GET.get('sort'))
        # Сортировка нужна в любом случае, поэтому она не в блоке if
        queryset = self._apply_sort_to_queryset(queryset)

        self.region_name = Region.objects.get(id=self.region_id)

        # ToDo Мне не нравятся эти два списка, так так это лишняя работа.
        # Вся необходимая информация есть уже в queryset
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
        else:
            context['type'] = 'all'

        return context
