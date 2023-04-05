import logging
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView

from travel.forms import VisitedCity_Create_Form
from travel.models import VisitedCity, City, Region
from utils.VisitedCityMixin import VisitedCityMixin

logger = logging.getLogger('app')


def prepare_log_string(status: int, message: str, request: WSGIRequest) -> str:
    """Возвращает строку, подготовленную для записи в log-файл"""
    return f'{status}: {message} URL: "{request.path}". Method: "{request.method}". User: "{request.user}"'


class VisitedCity_Create(LoginRequiredMixin, CreateView):
    """
    Отображает форму для добавления посещённого города и производит обработку этой формы.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """
    form_class = VisitedCity_Create_Form
    template_name = 'travel/visited_city/create.html'
    success_url = reverse_lazy('city-all')

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request

        return form_kwargs

    def form_valid(self, form):
        """
        Добавляет в данные формы ID авторизованного пользователя.
        """
        form.instance.user = self.request.user

        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['action'] = 'create'

        # Определяем предыдущую страницу для отображения в хлебных крошах
        if reverse('region-all') in self.request.META.get('HTTP_REFERER'):
            prev_page = ['region-all', 'Список регионов России']
        else:
            prev_page = ['city-all', 'Список посещённых городов']

        context['breadcrumb'] = [
            {'url': 'main_page', 'title': 'Главная', 'active': False},
            {'url': prev_page[0], 'title': prev_page[1], 'active': False},
            {'url': '', 'title': 'Добавление посещённого города', 'active': True}
        ]

        return context


class VisitedCity_Delete(LoginRequiredMixin, DeleteView):
    """
    Удаляет посещённый город, не отображая дополнительную страницу (подтверждение происходит в модальном окне).

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе dispatch).
       При попытке удалить непосещённый город - возвращаем ошибку 403.
    """
    model = VisitedCity
    success_url = reverse_lazy('city-all')

    def post(self, request, *args, **kwargs):
        try:
            VisitedCity.objects.get(user=self.request.user.pk, id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            logger.warning(
                prepare_log_string(404, 'Attempt to delete a non-existent record.', request),
                extra={'classname': self.__class__.__name__}
            )
            raise PermissionDenied()

        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Метод GET запрещён для данного класса."""
        logger.warning(
            prepare_log_string(403, 'Attempt to access the GET method..', request),
            extra={'classname': self.__class__.__name__}
        )
        raise PermissionDenied()


class VisitedCity_Update(LoginRequiredMixin, UpdateView):
    """
    Отображает страницу с формой для редактирования посещённого города, а также обрабатывает эту форму.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе dispatch).
       При попытке получить доступ к непосещённому городу - возвращаем ошибку 403.
    """
    model = VisitedCity
    form_class = VisitedCity_Create_Form
    template_name = 'travel/visited_city/create.html'
    success_url = reverse_lazy('city-all')

    def get(self, request, *args, **kwargs):
        try:
            VisitedCity.objects.get(user=self.request.user.pk, id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            logger.warning(
                prepare_log_string(404, 'Attempt to update a non-existent visited city.', request),
                extra={'classname': self.__class__.__name__}
            )
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request

        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['action'] = 'update'
        context['breadcrumb'] = [
            {'url': 'main_page', 'title': 'Главная', 'active': False},
            {'url': 'city-all', 'title': 'Список посещённых городов', 'active': False},
            {'url': '', 'title': 'Изменение посещённого города', 'active': True}
        ]

        return context


class VisitedCity_Detail(LoginRequiredMixin, DetailView):
    """
    Отображает страницу с информацией о посещённом городе.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе get).
       При попытке получить доступ к непосещённому городу - редирект на страницу со списком посещённых городов.
    """
    model = VisitedCity
    template_name = 'travel/visited_city/detail.html'

    def get(self, request, *args, **kwargs):
        try:
            VisitedCity.objects.get(
                user=self.request.user.pk,
                id=self.kwargs['pk']
            )
        except ObjectDoesNotExist:
            logger.warning(
                prepare_log_string(404, 'Attempt to access a non-existent visited city.', request),
                extra={'classname': self.__class__.__name__}
            )
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['action'] = 'create'
        context['breadcrumb'] = [
            {'url': 'main_page', 'title': 'Главная', 'active': False},
            {'url': 'city-all', 'title': 'Список посещённых городов', 'active': False},
            {'url': '', 'title': 'Информация о городе', 'active': True}
        ]

        return context


class VisitedCity_List(VisitedCityMixin, LoginRequiredMixin, ListView):
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


def _create_list_of_coordinates(cities: QuerySet) -> list:
    """
    Генерирует список с координатами городов формата ['width', longtude', 'city__title'], [...], ...
    """
    return [[
        str(city.city.coordinate_width),
        str(city.city.coordinate_longitude),
        city.city.title
    ] for city in cities]


def get_cities_based_on_region(request):
    """
    Возвращает список городов, связанных с указанным region_id,
    в формате HTML-страницы, содержащей валидные теги <option> для их использования в <select>.
    """
    region_id = request.GET.get('region')
    cities = City.objects.filter(region_id=region_id).order_by('title')

    return render(request, 'travel/visited_city/create_dropdown_list.html', {'cities': cities})
