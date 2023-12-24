import logging
from typing import Any
from datetime import datetime

from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.db.models import QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView

from city.forms import VisitedCity_Create_Form
from city.models import VisitedCity, City
from utils.VisitedCityMixin import VisitedCityMixin
from utils.LoggingMixin import LoggingMixin

logger = logging.getLogger('moi-goroda')


class VisitedCity_Create(LoginRequiredMixin, LoggingMixin, CreateView):
    """
    Отображает форму для добавления посещённого города и производит обработку этой формы.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """
    form_class = VisitedCity_Create_Form
    template_name = 'city/city_create.html'
    success_url = reverse_lazy('city-all-list')

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request

        return form_kwargs

    def form_valid(self, form):
        """
        Добавляет в данные формы ID авторизованного пользователя.
        """
        form.instance.user = self.request.user
        self.set_message(self.request, f'Creating a visited city')
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        context['active_page'] = 'add_city'
        context['page_title'] = 'Добавление города'
        context['page_description'] = 'Добавление нового посещённого города'

        return context


class VisitedCity_Delete(LoginRequiredMixin, LoggingMixin, DeleteView):
    """
    Удаляет посещённый город, не отображая дополнительную страницу (подтверждение происходит в модальном окне).

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе dispatch).
       При попытке удалить непосещённый город - возвращаем ошибку 403.
    """
    model = VisitedCity
    success_url = reverse_lazy('city-all-list')

    def post(self, request, *args, **kwargs):
        try:
            VisitedCity.objects.get(user=self.request.user.pk, id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            self.set_message(self.request, f'Attempt to delete a non-existent visited city #{self.kwargs["pk"]}')
            raise PermissionDenied()
        else:
            self.set_message(self.request, f'Deleting the visited city #{self.kwargs["pk"]}')

        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Метод GET запрещён для данного класса."""
        self.set_message(self.request, f'Attempt to access the GET method')
        raise PermissionDenied()


class VisitedCity_Update(LoginRequiredMixin, LoggingMixin, UpdateView):
    """
    Отображает страницу с формой для редактирования посещённого города, а также обрабатывает эту форму.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе dispatch).
       При попытке получить доступ к непосещённому городу - возвращаем ошибку 403.
    """
    model = VisitedCity
    form_class = VisitedCity_Create_Form
    template_name = 'city/city_create.html'

    def get(self, request, *args, **kwargs):
        try:
            VisitedCity.objects.get(user=self.request.user.pk, id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            self.set_message(self.request, f'Attempt to update a non-existent visited city #{self.kwargs["pk"]}')
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request

        return form_kwargs

    def get_success_url(self):
        return reverse_lazy('city-selected', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        self.set_message(self.request, f'Updating the visited city #{self.kwargs["pk"]}')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'update'
        context['page_title'] = 'Изменение города'
        context['page_description'] = 'Изменение посещённого города'

        return context


class VisitedCity_Detail(LoginRequiredMixin, LoggingMixin, DetailView):
    """
    Отображает страницу с информацией о посещённом городе.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе get).
       При попытке получить доступ к непосещённому городу - редирект на страницу со списком посещённых городов.
    """
    model = VisitedCity
    template_name = 'city/city_selected.html'

    def __init__(self):
        super().__init__()

        # Список коллекций, в которых состоит запрошенный город
        self.collections_list = None
        self.city_title: str = ''

    def get(self, request, *args, **kwargs):
        try:
            queryset = VisitedCity.objects.get(
                user=self.request.user.pk,
                id=self.kwargs['pk']
            )

            self.collections_list = City.objects.get(id=queryset.city.id).collections_list.all()
        except ObjectDoesNotExist:
            self.set_message(self.request, f'Attempt to access a non-existent visited city #{self.kwargs["pk"]}')
            raise Http404
        else:
            self.set_message(self.request, f'Viewing the visited city #{self.kwargs["pk"]}')

        self.city_title = queryset
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['collections_list'] = self.collections_list
        context['page_title'] = self.city_title
        context['page_description'] = f'Информация про посещённый город - {self.city_title}'

        return context


class VisitedCity_List(VisitedCityMixin, LoginRequiredMixin, LoggingMixin, ListView):
    """
    Отображает список всех посещённых городов пользователя.

    Фильтрация городов передаётся через GET-параметр `filter` и может принимать одно из следующих значений:
        * `magnet` - наличие магнита
        * `current_year` - посещённые в текущем году
        * `last_yesr` - посещённые в прошлом году

    Фильтрация городов передаётся через GET-параметр `sort` и может принимать одно из следующих значений:
        * `name_down` - по возрастанию имени
        * `name_up` - по убыванию имени
        * `date_down` - по возрастанию даты посещений
        * `date_up` - по убыванию даты посещения

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """
    model = VisitedCity
    paginate_by = 16

    all_cities = None
    list_or_map: str = ''

    def __init__(self, list_or_map: str):
        super().__init__()

        self.sort: str = ''
        self.filter: str = ''
        self.list_or_map = list_or_map
        self.total_qty_of_cities: int = 0
        self.qty_of_visited_cities: int = 0
        self.qty_of_visited_cities_current_year: int = 0
        self.qty_of_visited_cities_last_year: int = 0

    def get_queryset(self) -> QuerySet[dict]:
        """
        Получает из базы данных все посещённые города пользователя.
        Возвращает Queryset, состоящий из полей:
            * `id` - ID посещённого города
            * `date_of_visit` - дата посещения города
            * `rating` - рейтинг посещённого города
            * `has_magnet` - наличие магните
            * `city.id` - ID города
            * `city.title` - Название города
            * `city.population` - население города
            * `city.date_of_foundation` - дата основания города
            * `city.coordinate_width` - широта
            * `city.coordinate_longitude` - долгота
            * `region.id` - ID региона, в котором расположен город
            * `region.title` - название региона, в котором расположен город
            * `region.type` - тип региона, в котором расположен город
            (для отображение названия региона лучше использовать просто `region`,
            а не `region.title` и `region.type`, так как `region` через __str__()
            отображает корректное обработанное название)
        """
        queryset = VisitedCity.objects.filter(
            user=self.request.user
        ).select_related(
            'city', 'region'
        ).only(
            'id', 'date_of_visit', 'rating', 'has_magnet',
            'city__id', 'city__title', 'city__population', 'city__date_of_foundation',
            'city__coordinate_width', 'city__coordinate_longitude',
            'region__id', 'region__title', 'region__type'
        )

        self.total_qty_of_cities = City.objects.count()
        self.qty_of_visited_cities = queryset.count()
        self.qty_of_visited_cities_current_year = queryset.filter(date_of_visit__year=datetime.now().year).count()
        self.qty_of_visited_cities_last_year = queryset.filter(date_of_visit__year=datetime.now().year - 1).count()

        if self.list_or_map == 'list':
            self.set_message(self.request, 'Viewing the list of visited queryset')
        else:
            self.set_message(self.request, 'Viewing the map of visited queryset')

        # Обработка фильтрации
        self.filter = self.request.GET.get('filter') if self.request.GET.get('filter') else ''
        if self.filter:
            try:
                queryset = self.apply_filter_to_queryset(queryset, self.filter)
                self.set_message(self.request, f'Using filtering \'{self.filter}\'')
            except KeyError:
                logger.warning(f"Unexpected value of the GET-parametr 'filter' - {self.filter}")

        # Обработка сортировки
        sort_default = 'default'
        self.sort = self.request.GET.get('sort') if self.request.GET.get('sort') else sort_default
        try:
            queryset = self.apply_sort_to_queryset(queryset, self.sort)
            if self.sort != 'default':
                self.set_message(self.request, f'Using sorting \'{self.sort}\'')
        except KeyError:
            logger.warning(f"Unexpected value of the GET-param 'sort' - {self.sort}")
            queryset = self.apply_sort_to_queryset(queryset, sort_default)
            self.sort = ''

        # Дополнительная переменная нужна, так как используется пагинация и Django на уровне SQL-запроса
        # устанавливает лимит на выборку, равный `paginate_by`.
        # Из-за этого на карте отображается только `paginate_by` городов.
        # Чтобы отображались все города - используем доп. переменную без лимита.
        self.all_cities = queryset

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['all_cities'] = self.all_cities
        context['total_qty_of_cities'] = self.total_qty_of_cities
        context['qty_of_visited_cities'] = self.qty_of_visited_cities
        context['qty_of_visited_cities_current_year'] = self.qty_of_visited_cities_current_year
        context['qty_of_visited_cities_last_year'] = self.qty_of_visited_cities_last_year
        context['declension_of_total_cities'] = self.declension_of_city(self.total_qty_of_cities)
        context['declension_of_visited_cities'] = self.declension_of_city(self.qty_of_visited_cities)
        context['declension_of_visited'] = self.declension_of_visited(self.qty_of_visited_cities)

        context['filter'] = self.filter
        context['sort'] = self.sort

        context['active_page'] = 'city_list' if self.list_or_map == 'list' else 'city_map'
        context['url_for_filter_magnet'] = self.get_url_params(
            'magnet' if self.filter != 'magnet' else '',
            self.sort
        )
        context['url_for_filter_current_year'] = self.get_url_params(
            'current_year' if self.filter != 'current_year' else '',
            self.sort
        )
        context['url_for_filter_last_year'] = self.get_url_params(
            'last_year' if self.filter != 'last_year' else '',
            self.sort
        )
        context['url_for_sort_name_down'] = self.get_url_params(self.filter, 'name_down')
        context['url_for_sort_name_up'] = self.get_url_params(self.filter, 'name_up')
        context['url_for_sort_date_down'] = self.get_url_params(self.filter, 'date_down')
        context['url_for_sort_date_up'] = self.get_url_params(self.filter, 'date_up')

        if self.list_or_map == "list":
            context['page_title'] = 'Список посещённых городов'
            context['page_description'] = 'Список всех посещённых городов, отсортированный в порядке посещения'
        else:
            context['page_title'] = 'Карта посещённых городов'
            context['page_description'] = 'Карта с отмеченными посещёнными городами'

        return context

    def get_template_names(self) -> list[str]:
        if self.list_or_map == 'list':
            return ['city/city_all__list.html', ]
        elif self.list_or_map == 'map':
            return ['city/city_all__map.html', ]


def get_cities_based_on_region(request):
    """
    Возвращает список городов, связанных с указанным region_id,
    в формате HTML-страницы, содержащей валидные теги <option> для их использования в <select>.
    """
    region_id = request.GET.get('region')
    try:
        cities = City.objects.filter(region_id=region_id).order_by('title')
    except ValueError:
        cities = None
    return render(request, 'city/city_create__dropdown_list.html', {'queryset': cities})
