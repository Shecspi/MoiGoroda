"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, NoReturn, Callable

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.forms import BaseModelForm
from django.http import Http404, HttpResponse, HttpRequest, HttpResponseBase
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
from city.models import (
    City,
    CityListDefaultSettings,
    VisitedCity,
    CityDistrict,
    VisitedCityDistrict,
)
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


class VisitedCity_Create(LoginRequiredMixin, CreateView):  # type: ignore[type-arg]
    """
    Отображает форму для добавления посещённого города и производит обработку этой формы.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
    """

    form_class = VisitedCity_Create_Form
    template_name = 'city/create/page.html'
    success_url = reverse_lazy('city-all-list')

    def get_initial(self) -> dict[str, Any]:
        """
        В случае, когда в URL передан city_id, необходимо определить город и автоматически выбрать его в форме
        """
        initial = super().get_initial()
        city_id = self.request.GET.get('city_id')

        if city_id:
            try:
                city_id_int = int(city_id)
            except (ValueError, TypeError):
                logger.warning(
                    self.request,
                    f'(Visited city) Invalid city_id passed: {self.request.GET.get("city_id")}',
                )
                return initial

            try:
                city = City.objects.get(id=city_id_int)
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

    def form_valid(self, form: BaseModelForm) -> HttpResponse:  # type: ignore[type-arg]
        """
        Добавляет в данные формы ID авторизованного пользователя.
        """
        form.instance.user = self.request.user
        response = super().form_valid(form)

        if self.object and isinstance(self.request.user, AbstractBaseUser):
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
        return str(
            reverse_lazy(
                'city-selected',
                kwargs={'pk': VisitedCity.objects.get(pk=self.kwargs['pk']).city.pk},
            )
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        user_id = self.request.user.pk
        if user_id is None or not get_visited_city(user_id, self.kwargs['pk']):
            logger.warning(
                self.request,
                f'(Visited city) Attempt to delete a non-existent visited city #{self.kwargs["pk"]}',
            )
            raise Http404

        self.object = self.get_object()

        logger.info(self.request, f'(Visited city) Deleting the visited city #{self.kwargs["pk"]}')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form: Any) -> HttpResponse:
        """Выполняет удаление объекта и дополнительную логику обновления флагов посещения."""
        response = super().form_valid(form)
        if isinstance(self.request.user, AbstractBaseUser):
            set_is_visit_first_for_all_visited_cities(self.object.city_id, self.request.user)

        return response

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> NoReturn:
        """Метод GET запрещён для данного класса."""
        logger.warning(self.request, '(Visited city) Attempt to access the GET method')
        raise PermissionDenied()


class VisitedCity_Update(LoginRequiredMixin, UpdateView):  # type: ignore[type-arg]
    """
    Отображает страницу с формой для редактирования посещённого города, а также обрабатывает эту форму.

     > Доступ только для авторизованных пользователей (LoginRequiredMixin).
     > Доступ только к тем городам, которые пользователь уже посетил (обрабатывается в методе get_object).
       При попытке получить доступ к непосещённому городу - возвращаем ошибку 404.
    """

    model = VisitedCity
    form_class = VisitedCity_Create_Form
    template_name = 'city/create/page.html'

    def get_object(self, queryset: QuerySet[VisitedCity] | None = None) -> VisitedCity:
        """Получаем объект и проверяем, что он принадлежит текущему пользователю."""
        obj: VisitedCity = super().get_object(queryset)
        if obj.user != self.request.user:
            logger.warning(
                self.request,
                f'(Visited city) Attempt to update a non-existent visited city #{self.kwargs["pk"]}',
            )
            raise Http404
        return obj

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

    def form_valid(self, form: BaseModelForm) -> HttpResponse:  # type: ignore[type-arg]
        response = super().form_valid(form)
        if isinstance(self.request.user, AbstractBaseUser):
            set_is_visit_first_for_all_visited_cities(self.object.city_id, self.request.user)

        return response

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['action'] = 'update'
        context['page_title'] = 'Изменение города'
        context['page_description'] = 'Изменение посещённого города'

        return context


class VisitedCityDetail(DetailView):  # type: ignore[type-arg]
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
    template_name = 'city/detail/page.html'
    context_object_name = 'city'

    service: AbstractVisitedCityService | None = None
    service_factory: Callable[[HttpRequest], AbstractVisitedCityService] | None = None

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
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
        if self.service is None:
            raise ImproperlyConfigured('Service is not initialized')

        city_dto = self.service.get_city_details(self.kwargs['pk'], self.request.user)  # type: ignore[arg-type]

        context = super().get_context_data(**kwargs)
        context = {
            **context,
            **asdict(city_dto),
            'page_title': city_dto.page_title,
            'page_description': city_dto.page_description,
        }

        return context


class VisitedCity_Map(LoginRequiredMixin, TemplateView):
    template_name = 'city/map/page.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # Если в URL передан несуществующий код страны, то перенаправляем пользователя на страницу всех городов
        country_code = self.request.GET.get('country')
        if country_code and not Country.objects.filter(code=country_code).exists():
            return redirect('city-all-map')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list: Any = None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        country_code = self.request.GET.get('country')
        # country_code уже проверен на существование, здесь Country.DoesNotExist не может быть
        country = str(Country.objects.get(code=country_code)) if country_code else ''

        logger.info(self.request, '(Visited city) Viewing the map of visited cities')

        user_id = self.request.user.pk
        if user_id is None:
            raise Http404('User must be authenticated')

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
            f'Карта посещённых городов в {to_prepositional(country)}'
            if country
            else 'Карта посещённых городов'
        )
        context['page_description'] = 'Карта с отмеченными посещёнными городами'

        return context


class VisitedCity_List(LoginRequiredMixin, ListView):  # type: ignore[type-arg]
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
    template_name = 'city/list/page.html'

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
        self.default_filter_settings: CityListDefaultSettings | None = None
        self.default_sort_settings: CityListDefaultSettings | None = None

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # Если в URL передан несуществующий код страны, то перенаправляем пользователя на страницу всех городов
        country_code = self.request.GET.get('country')
        if country_code and not Country.objects.filter(code=country_code).exists():
            return redirect('city-all-map')

        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[VisitedCity]:
        self.user_id = self.request.user.pk
        if self.user_id is None:
            raise Http404('User must be authenticated')

        # Получаем сохранённые настройки по умолчанию
        self.default_filter_settings = CityListDefaultSettings.objects.filter(
            user_id=self.user_id, parameter_type='filter'
        ).first()
        self.default_sort_settings = CityListDefaultSettings.objects.filter(
            user_id=self.user_id, parameter_type='sort'
        ).first()

        # Используем GET-параметры, если они есть, иначе используем сохранённые настройки по умолчанию
        self.filter = self.request.GET.get('filter')
        if not self.filter and self.default_filter_settings:
            self.filter = self.default_filter_settings.parameter_value

        self.country_code = self.request.GET.get('country')

        if self.country_code:
            # country_code уже проверен на существование, здесь Country.DoesNotExist не может быть
            self.country = str(Country.objects.get(code=self.country_code))

        self.queryset = get_unique_visited_cities(self.user_id, self.country_code)
        self.apply_filter()
        self.apply_sort(
            self.default_sort_settings.parameter_value if self.default_sort_settings else None
        )

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
        if self.filter and self.queryset is not None and self.user_id is not None:
            try:
                self.queryset = apply_filter_to_queryset(self.queryset, self.user_id, self.filter)
            except KeyError:
                logger.warning(
                    self.request, f"(Region) Unexpected value of the filter '{self.filter}'"
                )

    def apply_sort(self, default_sort: str | None = None) -> None:
        # Используем GET-параметр, если он есть, иначе используем переданное значение по умолчанию или стандартное
        self.sort = self.request.GET.get('sort')
        if not self.sort:
            self.sort = default_sort if default_sort else 'last_visit_date_down'

        if self.queryset is not None and self.sort is not None:
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

    def get_context_data(self, *, object_list: Any = None, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.user_id is None:
            raise Http404('User must be authenticated')

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
            f'Список посещённых городов в {to_prepositional(self.country)}'
            if self.country
            else 'Список посещённых городов'
        )
        context['page_description'] = (
            'Список всех посещённых городов, отсортированный в порядке посещения'
        )

        # Используем сохранённые настройки по умолчанию из атрибутов класса
        context['default_filter'] = (
            self.default_filter_settings.parameter_value if self.default_filter_settings else None
        )
        context['default_sort'] = (
            self.default_sort_settings.parameter_value if self.default_sort_settings else None
        )

        return context


def get_cities_based_on_region(request: HttpRequest) -> HttpResponse:
    """
    Возвращает список городов, связанных с указанным region_id,
    в формате HTML-страницы, содержащей валидные теги <option> для их использования в <select>.
    """
    region_id = request.GET.get('region')
    try:
        cities = City.objects.filter(region_id=region_id).order_by('title')  # type: ignore[misc]
    except ValueError:
        logger.info(request, "(Visited city) Couldn't find cities in the requested region")
        cities = None
    return render(request, 'city/create/dropdown_list.html', {'cities': cities})


class CityDistrictMapView(TemplateView):
    """
    Отображает страницу с картой районов выбранного города.

    Доступна всем пользователям (авторизованным и неавторизованным).
    """

    template_name = 'city/districts/map/page.html'

    def __init__(self) -> None:
        super().__init__()
        self._city: City | None = None

    def _get_city(self) -> City:
        """
        Возвращает город по id из URL или выбрасывает Http404.
        """
        if self._city is not None:
            return self._city

        city_id = self.kwargs.get('city_id')
        if city_id is None:
            raise Http404('ID города не указан')

        try:
            city_id_int = int(city_id)
        except (TypeError, ValueError):
            raise Http404('Некорректный ID города')

        try:
            self._city = City.objects.select_related('country', 'region').get(pk=city_id_int)
            return self._city
        except City.DoesNotExist:
            raise Http404(f'Город с id {city_id} не найден')

    @staticmethod
    def _get_region_code(city: City) -> str | None:
        """
        Возвращает код региона из iso3166, если формат корректен.
        """
        if not city.region or not city.region.iso3166:
            return None

        parts = city.region.iso3166.split('-', maxsplit=1)
        if len(parts) != 2:
            return None

        return parts[1] or None

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Обрабатывает GET запрос. Проверяет существование города.
        """
        self._get_city()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)

        city = self._get_city()
        city_id = city.pk

        # Подсчитываем количество районов и посещённых районов
        qty_of_districts = CityDistrict.objects.filter(city=city).count()
        qty_of_visited_districts = 0
        if self.request.user.is_authenticated:
            qty_of_visited_districts = VisitedCityDistrict.objects.filter(
                user=self.request.user, city_district__city=city
            ).count()

        context['city'] = city
        context['city_id'] = city_id
        context['country_code'] = city.country.code
        context['city_name'] = city.title
        context['region_code'] = self._get_region_code(city)
        context['url_geo_polygons'] = settings.URL_GEO_POLYGONS
        context['is_authenticated'] = self.request.user.is_authenticated
        context['qty_of_districts'] = qty_of_districts
        context['qty_of_visited_districts'] = qty_of_visited_districts
        context['api_districts_url'] = reverse(
            'api__get_city_districts', kwargs={'city_id': city_id}
        )
        context['api_visit_url'] = reverse('api__add_visited_city_district')
        context['api_visit_delete_url'] = reverse('api__delete_visited_city_district')
        context['api_cities_url'] = reverse('api__get_cities_with_districts')

        context['active_page'] = 'city_districts_map'
        context['page_title'] = f'Карта районов города {city.title}'
        context['page_description'] = f'Интерактивная карта районов города {city.title}'

        logger.info(
            self.request,
            f'(City districts) Viewing districts map for city {city.title} (id: {city_id})',
        )

        return context
