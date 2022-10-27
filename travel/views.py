from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import QuerySet, Count, Q, Sum, Avg
from django.http import HttpResponseForbidden, Http404, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView

from travel.forms import VisitedCity_Create_Form
from travel.models import VisitedCity, City, Region


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
        context['prev_url'] = self.request.META.get('HTTP_REFERER')
        context['breadcrumb'] = [
            {'url': 'main_page', 'title': 'Главная', 'active': False},
            {'url': 'city-all', 'title': 'Список посещённых городов', 'active': False},
            {'url': '', 'title': 'Добавление посещённого города', 'active': True}
        ]

        return context


class VisitedCity_Delete(LoginRequiredMixin, DeleteView):
    """
    Удаляет посещённый город, не отображая дополнительную страницу (подтверждение происходит в модальном окне).

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе dispatch).
       При попытке удалить непосещённый город - редирект на страницу со списком посещённых городов.
    """
    model = VisitedCity
    success_url = reverse_lazy('city-all')

    def post(self, request, *args, **kwargs):
        try:
            VisitedCity.objects.get(user=self.request.user.pk, id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return HttpResponseForbidden()

        return super().post(request, *args, **kwargs)


class VisitedCity_Update(LoginRequiredMixin, UpdateView):
    """
    Отображает страницу с формой для редактирования посещённого города, а также обрабатывает эту форму.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе dispatch).
       При попытке получить доступ к непосещённому городу - редирект на страницу со списком посещённых городов.
    """
    model = VisitedCity
    form_class = VisitedCity_Create_Form
    template_name = 'travel/visited_city/create.html'
    success_url = reverse_lazy('city-all')

    def get(self, request, *args, **kwargs):
        try:
            VisitedCity.objects.get(user=self.request.user.pk, id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

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
            VisitedCity.objects.get(user=self.request.user.pk, id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

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


class VisitedCity_List(LoginRequiredMixin, ListView):
    """
    Отображает список посещённых городов пользователя, а конкретно:
        * все посещённые города, если в URL-запросе не указан параметр 'pk'
        * посещённые города конкретного региона, если параметр 'pk' указан.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """
    model = VisitedCity
    paginate_by = 15
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

    def get(self, *args, **kwargs):
        if self.kwargs:
            self.region_id = self.kwargs['pk']

            # При обращении к несуществующему региону выдаём 404
            # При этом в указанном регионе может не быть посещённых городов, это ок
            try:
                Region.objects.get(id=self.region_id)
            except ObjectDoesNotExist:
                return HttpResponseNotFound()

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

        # Обработка фильтров и сортировок из URL.
        if self.request.GET.get('filter'):
            match self.request.GET.get('filter'):
                case 'magnet':
                    queryset = queryset.filter(has_magnet=False)
                    self.filter = 'magnet'
                case 'current_year':
                    queryset = queryset.filter(date_of_visit__year=datetime.now().year)
                    self.filter = 'current_year'
                case 'last_year':
                    queryset = queryset.filter(date_of_visit__year=datetime.now().year-1)
                    self.filter = 'last_year'
                case _:
                    self.filter = None

        if self.request.GET.get('sort'):
            match self.request.GET.get('sort'):
                case 'name_down':
                    queryset = queryset.order_by('city__title')
                    self.sort = 'name_down'
                case 'name_up':
                    queryset = queryset.order_by('-city__title')
                    self.sort = 'name_up'
                case 'date_down':
                    queryset = queryset.order_by('date_of_visit')
                    self.sort = 'date_down'
                case 'date_up':
                    queryset = queryset.order_by('-date_of_visit')
                    self.sort = 'date_up'
                case _:
                    queryset = queryset.order_by('-date_of_visit', 'city__title')
        else:
            queryset = queryset.order_by('-date_of_visit', 'city__title')

        # Если в URL указан ID региона, то отображаем только посещённые города в этом регионе.
        if self.region_id:
            queryset = queryset.filter(region_id=self.region_id)

            # Имя региона
            self.region_name = Region.objects.get(id=self.region_id)

            # Список с координатами посещённых городов
            self.coords_of_visited_cities = _create_list_of_coordinates(queryset)

            # Список с координатами непосещённых городов
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


class Region_List(LoginRequiredMixin, ListView):
    """
    Отображает список всех регионов с указанием количества посещённых городов в каждом.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """
    model = Region
    paginate_by = 15
    template_name = 'travel/region/list.html'
    all_regions = []

    def get_queryset(self):
        self.all_regions = Region.objects.all().annotate(
            num_visited=Count('city', filter=Q(city__visitedcity__user=self.request.user.pk), distinct=True)
        )

        return Region.objects.all().annotate(
            num_total=Count('city', distinct=True),
            num_visited=Count('city', filter=Q(city__visitedcity__user=self.request.user.pk), distinct=True)
        ).order_by('-num_visited', 'title')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['all_regions'] = self.all_regions
        context['breadcrumb'] = [
            {'url': 'main_page', 'title': 'Главная', 'active': False},
            {'url': '', 'title': 'Список регионов России', 'active': True}
        ]

        return context


def _create_list_of_coordinates(cities: list) -> list:
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
