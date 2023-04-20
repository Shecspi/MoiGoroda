from django.http import Http404
from django.views.generic import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Exists, OuterRef, Subquery
from django.db.models import QuerySet, BooleanField, DateField, IntegerField

from region.models import Region
from city.models import VisitedCity, City
from city.views import logger, prepare_log_string
from utils.VisitedCityMixin import VisitedCityMixin
from utils.sort_funcs import sort_validation, apply_sort
from utils.filter_funcs import filter_validation, apply_filter


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
    Отображает список все городов в указанном регионе, как посещённых, так и нет.

    Фильтрация городов передаётся через GET-параметр `filter` и может принимать одно из следующих значений:
        * `magnet` - наличие магнита
        * `current_year` - посещённые в текущем году
        * `last_yesr` - посещённые в прошлом году

    Фильтрация городов передаётся через GET-параметр `sort` и может принимать одно из следующих значений:
        * `name_down` - по возрастанию имени
        * `name_up` - по убыванию имени
        * `date_down` - по возрастанию даты посещений
        * `date_up` - по убыванию даты посещения

    На эту страницу имеют доступ только авторизованные пользователи (LoginRequiredMixin).
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
        except ObjectDoesNotExist:
            logger.warning(
                prepare_log_string(404, 'Attempt to update a non-existent region.', self.request),
                extra={'classname': self.__class__.__name__}
            )
            raise Http404

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
            * `visited_id` - ID посещённого города
            * `date_of_visit` - дата посещения
            * `has_magnet` - True, если имеется магнит
            * `rating` - рейтинг от 1 до 5
        """
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

        # Дополнительная переменная нужна, так как используется пагинация и Django на уровне SQL-запроса
        # устанавливает лимит на выборку, равный `paginate_by`.
        # Из-за этого на карте отображается только `paginate_by` городов.
        # Чтобы отображались все города - используем доп. переменную без лимита.
        self.all_cities = queryset

        if self.request.GET.get('filter'):
            filter_value = self.request.GET.get('filter')
            self.filter = filter_validation(filter_value, self.valid_filters)
            if self.filter:
                queryset = apply_filter(queryset, filter_value)

        sort_value = ''
        if self.request.GET.get('sort'):
            sort_value = self.request.GET.get('sort')
            self.sort = sort_validation(sort_value, self.valid_sorts)
        # Сортировка нужна в любом случае, поэтому она не в блоке if
        queryset = apply_sort(queryset, sort_value)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['all_cities'] = self.all_cities
        context['filter'] = self.filter
        context['sort'] = self.sort
        context['type'] = 'by_region'
        context['region_id'] = self.region_id
        context['region_name'] = self.region_name

        return context
