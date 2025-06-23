"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any, NoReturn, Callable

from django.forms import BaseModelForm
from django.http import Http404, HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.db.models import QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.views.generic import (
    ListView,
    CreateView,
    DeleteView,
    UpdateView,
    DetailView,
    TemplateView,
)

from city.forms import VisitedCity_Create_Form
from city.models import VisitedCity, City
from city.services.db import (
    get_unique_visited_cities,
    set_is_visit_first_for_all_visited_cities,
    get_number_of_visited_countries,
)
from city.services.interfaces import AbstractVisitedCityService
from city.services.sort import apply_sort_to_queryset
from city.services.filter import apply_filter_to_queryset
from country.models import Country
from services import logger
from city.services.db import get_number_of_cities, get_number_of_new_visited_cities
from services.db.visited_city_repo import (
    get_visited_city,
)
from services.morphology import to_prepositional
from subscribe.repository import is_user_has_subscriptions, get_all_subscriptions


class VisitedCity_Create(LoginRequiredMixin, CreateView):
    """
    Отображает форму для добавления посещённого города и производит обработку этой формы.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """

    form_class = VisitedCity_Create_Form
    template_name = 'city/city_create.html'
    success_url = reverse_lazy('city-all-list')

    def get_initial(self) -> dict[str, Any]:
        """
        В случае, когда в URL передан city_id, необходимо определить город и автоматически выбрать его в форме
        """
        initial = super().get_initial()
        city_id = self.request.GET.get('city_id')

        if city_id:
            try:
                city_id = int(city_id)
            except (ValueError, TypeError):
                logger.warning(
                    self.request,
                    f'(Visited city) Invalid city_id passed: {self.request.GET.get('city_id')}',
                )
                return initial

            try:
                city = City.objects.get(id=city_id)
            except City.DoesNotExist:
                logger.warning(
                    self.request, f'(Visited city) City with id={city_id} does not exist'
                )
            else:
                initial['city'] = city.id
                initial['country'] = city.country.id
                if city.region:
                    initial['region'] = city.region.id

        return initial

    def get_form_kwargs(self) -> dict[str, Any]:
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """
        Добавляет в данные формы ID авторизованного пользователя.
        """
        form.instance.user = self.request.user
        response = super().form_valid(form)

        set_is_visit_first_for_all_visited_cities(self.object.city_id, self.request.user)

        logger.info(self.request, '(Visited city) Adding a visited city')
        return response

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

    def get_success_url(self) -> str:
        return reverse_lazy(
            'city-selected',
            kwargs={'pk': VisitedCity.objects.get(pk=self.kwargs['pk']).city.pk},
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not get_visited_city(self.request.user.pk, self.kwargs['pk']):
            logger.warning(
                self.request,
                f'(Visited city) Attempt to delete a non-existent visited city #{self.kwargs["pk"]}',
            )
            raise Http404

        self.object = self.get_object()
        self.city_id = self.object.city.id

        logger.info(self.request, f'(Visited city) Deleting the visited city #{self.kwargs["pk"]}')
        return self.delete(request, *args, **kwargs)

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().delete(request, *args, **kwargs)
        set_is_visit_first_for_all_visited_cities(self.object.city_id, self.request.user)

        return response

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

    def get_initial(self) -> dict[str, Any]:
        """
        Устанавливает значения формы по умолчанию.
        """
        initial = super().get_initial()

        # Проверка наличия города в базе не требуется, так как это уже сделано на уровне Django
        city_id = self.kwargs['pk']
        city = VisitedCity.objects.get(id=city_id)
        initial['city'] = city.city.id
        initial['country'] = city.city.country.id
        if city.city.region:
            initial['region'] = city.city.region.id

        return initial

    def get_form_kwargs(self) -> dict[str, Any]:
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs

    def get_success_url(self) -> str:
        logger.info(self.request, f'(Visited city) Updating the visited city #{self.kwargs["pk"]}')
        return reverse('city-selected', kwargs={'pk': self.object.city.id})

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        set_is_visit_first_for_all_visited_cities(self.object.city_id, self.request.user)

        return response

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['action'] = 'update'
        context['page_title'] = 'Изменение города'
        context['page_description'] = 'Изменение посещённого города'

        return context


class VisitedCity_Detail(DetailView):
    """
    Отображает детальную страницу с информацией о конкретном городе.

    Этот класс-наследник Django DetailView отвечает за:
    - загрузку объекта City по первичному ключу из URL;
    - получение подробных данных по городу через сервис `AbstractVisitedCityService`;
    - передачу этих данных в контекст шаблона для рендеринга страницы.

    Атрибуты:
        service (AbstractVisitedCityService): Экземпляр сервиса для работы с логикой города,
            инициализируется в методе dispatch.
        service_factory (Callable[[HttpRequest], AbstractVisitedCityService]): Фабрика для создания
            сервиса, принимающая запрос и возвращающая сервис. Должна быть обязательно установлена перед вызовом.
    """

    model = City
    template_name = 'city/city_selected.html'
    context_object_name = 'city'

    service: AbstractVisitedCityService = None
    service_factory: Callable[[HttpRequest], AbstractVisitedCityService] = None

    def dispatch(self, request, *args, **kwargs):
        """
        Переопределён для инициализации сервиса с помощью фабрики до обработки запроса.
        Проверяет наличие фабрики и создаёт сервис.
        """
        if not self.service_factory:
            raise ImproperlyConfigured('VisitedCityService factory is not set')
        self.service = self.service_factory(request)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует контекст для шаблона, расширяя базовый контекст данными,
        полученными из сервиса по деталям города и метаданным страницы.
        """
        city_id = self.kwargs['pk']
        city_dto = self.service.get_city_details(city_id, self.request.user)

        context = super().get_context_data(**kwargs)

        context = {
            **context,
            'page_title': city_dto.page_title,
            'page_description': city_dto.page_description,
            # ---
            'city': city_dto.city,
            'average_rating': city_dto.average_rating,
            'popular_months': ', '.join(city_dto.popular_months),
            'collections': city_dto.collections,
            'visits': city_dto.visits,
            'all_cities_qty': city_dto.all_cities_qty,
            'region_cities_qty': city_dto.region_cities_qty,
            'number_of_visits': city_dto.number_of_visits,
            'number_of_users_who_visit_city': city_dto.number_of_users_who_visit_city,
            'total_number_of_visits': city_dto.total_number_of_visits,
            # ---
            'visits_rank_in_country': city_dto.visits_rank_in_country,
            'users_rank_in_country': city_dto.users_rank_in_country,
            'visits_rank_in_region': city_dto.visits_rank_in_region,
            'users_rank_in_region': city_dto.users_rank_in_region,
            'users_rank_in_country_neighboring_cities': city_dto.users_rank_in_country_neighboring_cities,
            'visits_rank_in_country_neighboring_cities': city_dto.visits_rank_in_country_neighboring_cities,
            'users_rank_neighboring_cities_in_region': city_dto.users_rank_neighboring_cities_in_region,
            'visits_rank_neighboring_cities_in_region': city_dto.visits_rank_neighboring_cities_in_region,
        }

        return context


class VisitedCity_Map(LoginRequiredMixin, TemplateView):
    template_name = 'city/city_all__map.html'

    def get(self, request, *args, **kwargs):
        # Если в URL передан несуществующий код страны, то перенаправляем пользователя на страницу всех городов
        country_code = self.request.GET.get('country')
        if country_code and not Country.objects.filter(code=country_code).exists():
            return redirect('city-all-map')

        return super().get(request, *args, **kwargs)

    def get_context_data(
        self, *, object_list: QuerySet[dict] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        country_code = self.request.GET.get('country')
        # country_code уже проверен на существование, здесь Country.DoesNotExist не может быть
        country = str(Country.objects.get(code=country_code)) if country_code else ''

        logger.info(self.request, '(Visited city) Viewing the map of visited cities')

        user_id = self.request.user.pk

        number_of_cities = get_number_of_cities()
        number_of_visited_cities = get_number_of_new_visited_cities(user_id)
        number_of_cities_in_country = get_number_of_cities(country_code)
        number_of_visited_cities_in_country = get_number_of_new_visited_cities(
            user_id, country_code
        )
        number_of_visited_countries = get_number_of_visited_countries(user_id)

        context['total_qty_of_cities'] = number_of_cities
        context['qty_of_visited_cities'] = number_of_visited_cities
        context['number_of_cities_in_country'] = number_of_cities_in_country
        context['number_of_visited_cities_in_country'] = number_of_visited_cities_in_country
        context['number_of_visited_countries'] = number_of_visited_countries

        context['is_user_has_subscriptions'] = is_user_has_subscriptions(user_id)
        context['subscriptions'] = get_all_subscriptions(user_id)

        context['country_name'] = country
        context['country_code'] = country_code

        context['active_page'] = 'city_map'
        context['page_title'] = (
            f'Карта посещённых городов в {to_prepositional(country).title()}'
            if country
            else 'Карта посещённых городов'
        )
        context['page_description'] = 'Карта с отмеченными посещёнными городами'

        return context


class VisitedCity_List(LoginRequiredMixin, ListView):
    """
    Отображает список всех посещённых городов пользователя.

    Фильтрация городов передаётся через GET-параметр `filter` и может принимать одно из следующих значений:
        * `magnet` - наличие сувенира из города
        * `current_year` - посещённые в текущем году
        * `last_year` - посещённые в прошлом году

    Фильтрация городов передаётся через GET-параметр `sort` и может принимать одно из следующих значений:
        * `name_down` - по возрастанию имени
        * `name_up` - по убыванию имени
        * `date_down` - по возрастанию даты посещений
        * `date_up` - по убыванию даты посещения

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """

    model = VisitedCity
    paginate_by = 24
    template_name = 'city/city_all__list.html'

    all_cities = None

    def __init__(self) -> None:
        super().__init__()

        self.sort: str | None = ''
        self.filter: str | None = ''
        self.country: str = ''
        self.country_code: str | None = None
        self.user_id: int | None = None
        self.total_qty_of_cities: int = 0
        self.qty_of_visited_cities: int = 0
        self.has_subscriptions: bool = False
        self.all_visited_cities: QuerySet[VisitedCity] | None = None

    def get(self, request, *args, **kwargs):
        # Если в URL передан несуществующий код страны, то перенаправляем пользователя на страницу всех городов
        country_code = self.request.GET.get('country')
        if country_code and not Country.objects.filter(code=country_code).exists():
            return redirect('city-all-map')

        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[VisitedCity]:
        self.user_id = self.request.user.pk
        self.filter = self.request.GET.get('filter')
        self.country_code = self.request.GET.get('country')

        if self.country_code:
            # country_code уже проверен на существование, здесь Country.DoesNotExist не может быть
            self.country = str(Country.objects.get(code=self.country_code))

        self.queryset = get_unique_visited_cities(self.user_id, self.country_code)
        self.apply_filter()
        self.apply_sort()

        logger.info(self.request, '(Visited city) Viewing the list of visited cities')

        # Дополнительная переменная нужна, так как используется пагинация и Django на уровне SQL-запроса
        # устанавливает лимит на выборку, равный `paginate_by`.
        # Из-за этого на карте отображается только `paginate_by` городов.
        # Чтобы отображались все города - используем доп. переменную без лимита.
        self.all_cities = self.queryset

        return self.queryset

    def apply_filter(self) -> None:
        """
        Применяет фильтр к набору данных, если параметр `filter` указан.
        """
        if self.filter:
            try:
                self.queryset = apply_filter_to_queryset(self.queryset, self.user_id, self.filter)
            except KeyError:
                logger.warning(
                    self.request, f"(Region) Unexpected value of the filter '{self.filter}'"
                )

    def apply_sort(self) -> None:
        self.sort = (
            self.request.GET.get('sort') if self.request.GET.get('sort') else 'last_visit_date_down'
        )
        try:
            self.queryset = apply_sort_to_queryset(self.queryset, self.sort)
        except KeyError:
            logger.warning(
                self.request, f"(Visited city) Unexpected value of the sorting '{self.sort}'"
            )
            self.sort = 'last_visit_date_down'
        else:
            if self.sort != 'last_visit_date_down':
                logger.info(self.request, f"(Visited city) Using sorting '{self.sort}'")

    def get_context_data(
        self, *, object_list: QuerySet[dict] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        number_of_cities = get_number_of_cities()
        number_of_cities_in_country = get_number_of_cities(self.country_code)
        number_of_visited_cities = get_number_of_new_visited_cities(self.user_id)
        number_of_visited_cities_in_country = get_number_of_new_visited_cities(
            self.user_id, self.country_code
        )
        number_of_visited_countries = get_number_of_visited_countries(self.user_id)

        context['all_cities'] = self.all_cities
        context['total_qty_of_cities'] = number_of_cities
        context['number_of_cities_in_country'] = number_of_cities_in_country
        context['number_of_visited_cities_in_country'] = number_of_visited_cities_in_country
        context['number_of_visited_countries'] = number_of_visited_countries
        context['qty_of_visited_cities'] = number_of_visited_cities

        context['filter'] = self.filter
        context['sort'] = self.sort

        context['active_page'] = 'city_list'

        context['is_user_has_subscriptions'] = is_user_has_subscriptions(self.user_id)
        context['subscriptions'] = get_all_subscriptions(self.user_id)

        context['country_name'] = str(self.country)
        context['country_code'] = self.country_code
        context['page_title'] = (
            f'Список посещённых городов в {to_prepositional(self.country).title()}'
            if self.country
            else 'Список посещённых городов'
        )
        context['page_description'] = (
            'Список всех посещённых городов, отсортированный в порядке посещения'
        )

        return context


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
