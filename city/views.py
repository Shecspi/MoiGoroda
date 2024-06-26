"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any, NoReturn

from django.contrib.auth.models import User
from django.forms import BaseModelForm
from django.http import Http404, HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.db.models import QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView

from city.forms import VisitedCity_Create_Form
from city.models import VisitedCity, City
import city.structs as structs
from collection.models import Collection
from services import logger
from services.db.city_repo import get_number_of_cities, get_list_of_collections
from services.db.visited_city_repo import (
    get_all_visited_cities,
    get_visited_city,
    get_number_of_visited_cities,
    get_number_of_visited_cities_current_year,
    get_number_of_visited_cities_previous_year,
)
from services.word_modifications.city import modification__city
from services.word_modifications.visited import modification__visited
from subscribe.repository import is_user_has_subscriptions, get_all_subscriptions
from utils.VisitedCityMixin import VisitedCityMixin


class VisitedCity_Create(LoginRequiredMixin, CreateView):
    """
    Отображает форму для добавления посещённого города и производит обработку этой формы.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """

    form_class = VisitedCity_Create_Form
    template_name = 'city/city_create.html'
    success_url = reverse_lazy('city-all-list')

    def get_form_kwargs(self) -> dict[str, Any]:
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """
        Добавляет в данные формы ID авторизованного пользователя.
        """
        form.instance.user = self.request.user
        logger.info(self.request, '(Visited city) Adding a visited city')
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['action'] = 'create'
        context['active_page'] = 'add_city'
        context['page_title'] = 'Добавление города'
        context['page_description'] = 'Добавление нового посещённого города'

        return context


class VisitedCity_Delete(LoginRequiredMixin, DeleteView):  # type: ignore
    """
    Удаляет посещённый город, не отображая дополнительную страницу (подтверждение происходит в модальном окне).

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе dispatch).
       При попытке удалить непосещённый город - возвращаем ошибку 403.
    """

    model = VisitedCity
    success_url = reverse_lazy('city-all-list')

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not get_visited_city(self.request.user.pk, self.kwargs['pk']):
            logger.warning(
                self.request,
                f'(Visited city) Attempt to delete a non-existent visited city #{self.kwargs["pk"]}',
            )
            raise Http404
        logger.info(self.request, f'(Visited city) Deleting the visited city #{self.kwargs["pk"]}')
        return super().post(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> NoReturn:
        """Метод GET запрещён для данного класса."""
        logger.warning(self.request, '(Visited city) Attempt to access the GET method')
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
    template_name = 'city/city_create.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not get_visited_city(self.request.user.pk, self.kwargs['pk']):
            logger.warning(
                self.request,
                f'(Visited city) Attempt to update a non-existent visited city #{self.kwargs["pk"]}',
            )
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict[str, Any]:
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs

    def get_success_url(self) -> str:
        logger.info(self.request, f'(Visited city) Updating the visited city #{self.kwargs["pk"]}')
        return reverse('city-selected', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['action'] = 'update'
        context['page_title'] = 'Изменение города'
        context['page_description'] = 'Изменение посещённого города'

        return context


class VisitedCity_Detail(LoginRequiredMixin, DetailView):
    """
    Отображает страницу с информацией о посещённом городе.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе get).
       При попытке получить доступ к непосещённому городу - редирект на страницу со списком посещённых городов.
    """

    model = VisitedCity
    template_name = 'city/city_selected.html'

    def __init__(self) -> None:
        super().__init__()

        # Список коллекций, в которых состоит запрошенный город
        self.collections_list: QuerySet[Collection] | None = None
        self.city_title: str = ''

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if queryset := get_visited_city(self.request.user.pk, self.kwargs['pk']):
            self.collections_list = get_list_of_collections(queryset.city.id)
        else:
            logger.warning(
                self.request,
                f'(Visited city) Attempt to access a non-existent visited city #{self.kwargs["pk"]}',
            )
            raise Http404

        logger.info(self.request, f'(Visited city) Viewing the visited city #{self.kwargs["pk"]}')
        self.city_title = queryset.city.title

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['collections_list'] = self.collections_list
        context['page_title'] = self.city_title
        context['page_description'] = f'Информация про посещённый город - {self.city_title}'

        return context


class VisitedCity_List(VisitedCityMixin, LoginRequiredMixin, ListView):
    """
    Отображает список всех посещённых городов пользователя.

    Фильтрация городов передаётся через GET-параметр `filter` и может принимать одно из следующих значений:
        * `magnet` - наличие сувенира из города
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

    def __init__(self, list_or_map: str) -> None:
        super().__init__()

        self.sort: str | None = ''
        self.filter: str | None = ''
        self.list_or_map = list_or_map
        self.user_id: int | None = None
        self.total_qty_of_cities: int = 0
        self.qty_of_visited_cities: int = 0
        self.has_subscriptions: bool = False
        self.qty_of_visited_cities_last_year: int = 0
        self.qty_of_visited_cities_current_year: int = 0
        self.all_visited_cities: QuerySet[VisitedCity] | None = None

    def get_queryset(self) -> QuerySet[VisitedCity]:
        self.user_id = self.request.user.pk
        self.all_visited_cities = get_all_visited_cities(self.user_id)

        if self.list_or_map == 'list':
            logger.info(self.request, '(Visited city) Viewing the list of visited cities')
        else:
            logger.info(self.request, '(Visited city) Viewing the map of visited cities')

        # Обработка фильтрации
        self.filter = self.request.GET.get('filter') if self.request.GET.get('filter') else ''
        if self.filter:
            try:
                self.all_visited_cities = self.apply_filter_to_queryset(
                    self.all_visited_cities, self.filter
                )
                logger.info(self.request, f"(Visited city) Using the filter '{self.filter}'")
            except KeyError:
                logger.warning(
                    self.request, f"(Visited city) Unexpected value of the filter - '{self.filter}'"
                )

        # Обработка сортировки
        sort_default = 'default'
        self.sort = self.request.GET.get('sort') if self.request.GET.get('sort') else sort_default
        try:
            self.all_visited_cities = self.apply_sort_to_queryset(
                self.all_visited_cities, self.sort
            )
            if self.sort != 'default':
                logger.info(self.request, f"(Visited city) Using sorting '{self.sort}'")
        except KeyError:
            logger.info(
                self.request, f"(Visited city) Unexpected value of the sorting - '{self.sort}'"
            )
            self.all_visited_cities = self.apply_sort_to_queryset(
                self.all_visited_cities, sort_default
            )
            self.sort = ''

        # Дополнительная переменная нужна, так как используется пагинация и Django на уровне SQL-запроса
        # устанавливает лимит на выборку, равный `paginate_by`.
        # Из-за этого на карте отображается только `paginate_by` городов.
        # Чтобы отображались все города - используем доп. переменную без лимита.
        self.all_cities = self.all_visited_cities

        return self.all_visited_cities

    def get_context_data(
        self, *, object_list: QuerySet[dict] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        number_of_cities = get_number_of_cities()
        number_of_visited_cities = get_number_of_visited_cities(self.user_id)

        context['all_cities'] = self.all_cities
        context['total_qty_of_cities'] = number_of_cities
        context['qty_of_visited_cities'] = number_of_visited_cities
        context['qty_of_visited_cities_current_year'] = get_number_of_visited_cities_current_year(
            self.user_id
        )
        context['qty_of_visited_cities_last_year'] = get_number_of_visited_cities_previous_year(
            self.user_id
        )
        context['declension_of_total_cities'] = modification__city(number_of_cities)
        context['declension_of_visited_cities'] = modification__city(number_of_visited_cities)
        context['declension_of_visited'] = modification__visited(number_of_visited_cities)

        context['filter'] = self.filter
        context['sort'] = self.sort

        context['active_page'] = 'city_list' if self.list_or_map == 'list' else 'city_map'
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

        context['is_user_has_subscriptions'] = is_user_has_subscriptions(self.user_id)
        context['subscriptions'] = get_all_subscriptions(self.user_id)

        if self.list_or_map == 'list':
            context['page_title'] = 'Список посещённых городов'
            context['page_description'] = (
                'Список всех посещённых городов, отсортированный в порядке посещения'
            )
        else:
            context['page_title'] = 'Карта посещённых городов'
            context['page_description'] = 'Карта с отмеченными посещёнными городами'

        return context

    def get_template_names(self) -> list[str] | NoReturn:
        if self.list_or_map == 'list':
            return [
                'city/city_all__list.html',
            ]
        elif self.list_or_map == 'map':
            return [
                'city/city_all__map.html',
            ]
        else:
            logger.info(self.request, '(Visited city) Can not determine which template to display')
            raise Http404


def get_cities_based_on_region(request: HttpRequest) -> HttpResponse:
    """
    Возвращает список городов, связанных с указанным region_id,
    в формате HTML-страницы, содержащей валидные теги <option> для их использования в <select>.
    """
    region_id = request.GET.get('region')
    try:
        cities = City.objects.filter(region_id=region_id).order_by('title')
    except ValueError:
        logger.info(request, "(Visited city) Couldn't find cities in the requested region")
        cities = None
    return render(request, 'city/city_create__dropdown_list.html', {'cities': cities})


def get_struct_city(user_id: int) -> list[structs.City]:
    own_cities = []

    for city in get_all_visited_cities(user_id):
        coordinates = structs.Coordinates(
            lat=city.city.coordinate_width, lon=city.city.coordinate_longitude
        )
        city = structs.City(title=city.city.title, coordinates=coordinates)
        own_cities.append(city)

    return own_cities


def get_struct_subscription_cities(user_ids: list) -> list[structs.SubscriptionCities]:
    subscriptions_cities = []

    for user_id in user_ids:
        username = User.objects.get(pk=user_id).username
        visited_cities = get_struct_city(user_id)
        subscriptions_cities.append(
            structs.SubscriptionCities(username=username, cities=visited_cities)
        )

    return subscriptions_cities


def get_users_cities(request: HttpRequest) -> JsonResponse:
    users_id = [2, 3]

    own_cities = get_struct_city(request.user.pk)
    subscriptions_cities = get_struct_subscription_cities(users_id)

    response = structs.CitiesResponse(own=own_cities, subscriptions=subscriptions_cities)

    return JsonResponse(data=response.model_dump_json(), safe=False)
