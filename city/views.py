"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any, NoReturn

from django.db.models.functions import Round
from django.forms import BaseModelForm
from django.http import Http404, HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.db.models import QuerySet, Avg, Count, F, OuterRef, Subquery
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
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
    get_number_of_users_who_visit_city,
    get_total_number_of_visits,
    get_rank_by_visits_of_city,
    get_neighboring_cities_by_users_rank,
    get_neighboring_cities_by_visits_rank,
    get_neighboring_cities_in_region_by_visits_rank,
    get_neighboring_cities_in_region_by_users_rank,
    get_rank_by_visits_of_city_in_region,
    get_rank_by_users_of_city_in_region,
    get_number_of_cities_in_region_by_city,
    get_rank_by_users_of_city,
    get_number_of_visited_countries,
)
from city.services.sort import apply_sort_to_queryset
from city.services.filter import apply_filter_to_queryset
from collection.models import Collection
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
    Отображает страницу с информацией о городе.
    """

    model = City
    template_name = 'city/city_selected.html'
    context_object_name = 'city'

    MONTH_NAMES = [
        '',
        'Январь',
        'Февраль',
        'Март',
        'Апрель',
        'Май',
        'Июнь',
        'Июль',
        'Август',
        'Сентябрь',
        'Октябрь',
        'Ноябрь',
        'Декабрь',
    ]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.city = None

    def get_object(self, queryset: QuerySet[City] = None) -> City:
        self.city = City.objects.annotate(
            average_rating=Round((Avg('visitedcity__rating') * 2), 0) / 2,
        )

        # Если пользователь залогинен — добавляем number_of_visits
        if self.request.user.is_authenticated:
            number_of_visits = (
                VisitedCity.objects.filter(city_id=OuterRef('pk'), user=self.request.user)
                .values('city')
                .annotate(count=Count('id'))
                .values('count')
            )
            self.city = self.city.annotate(number_of_visits=Subquery(number_of_visits))

        # Получаем сам объект города из QuerySet
        try:
            self.city = self.city.get(id=self.kwargs['pk'])
        except City.DoesNotExist:
            logger.warning(
                self.request,
                f'(Visited city) Attempt to access a non-existent city #{self.kwargs["pk"]}',
            )
            raise Http404

        popular_month = (
            VisitedCity.objects.filter(city=self.city, date_of_visit__isnull=False)
            .annotate(month=F('date_of_visit__month'))
            .values('month')
            .annotate(visits=Count('id'))
            .order_by('-visits')
        )
        self.city.popular_months = [
            self.MONTH_NAMES[month.get('month')] for month in popular_month[:3]
        ]

        if self.request.user.is_authenticated:
            self.city.visits = (
                VisitedCity.objects.filter(user=self.request.user, city=self.city)
                .order_by(F('date_of_visit').desc(nulls_last=True))
                .values('id', 'date_of_visit', 'rating', 'impression', 'city__title')
            )

        self.city.collections = Collection.objects.filter(city=self.city)

        self.city.number_of_visits_all_users = (
            VisitedCity.objects.filter(city=self.city.id)
            .aggregate(count=Count('*'))
            .get('count', 0)
        )

        logger.info(self.request, f'(Visited city) Viewing the visited city #{self.city.pk}')
        return self.city

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        country_id = self.city.country_id

        context['page_title'] = (
            f'{self.city.title}, {self.city.region}, {self.city.country} - информация о городе, карта'
            if self.city.region
            else f'{self.city.title}, {self.city.country} - информация о городе, карта'
        )

        context['page_description'] = (
            f'{self.city.title}, {self.city.country}, {self.city.region}. '
            if self.city.region
            else f'{self.city.title}, {self.city.country}. '
        )

        if len(self.city.collections) == 1:
            context['page_description'] += f"Входит в коллекцию '{self.city.collections[0]}'"
        elif len(self.city.collections) >= 2:
            context['page_description'] += (
                f"Входит в коллекции {', '.join(["«" + str(collection) + "»" for collection in self.city.collections])} "
            )

        if self.city.average_rating:
            context['page_description'] += (
                f'Средняя оценка путешественников — {self.city.average_rating}. '
            )

        if self.city.popular_months:
            context['page_description'] += (
                f"Лучшее время для поездки: {', '.join(sorted(self.city.popular_months, key=lambda m: self.MONTH_NAMES.index(m)))}. "
            )

        context['page_description'] += (
            'Смотрите информацию о городе и карту на сайте «Мои Города». '
            'Зарегистрируйтесь, чтобы отмечать посещённые города.'
        )

        context['number_of_users_who_visit_city'] = get_number_of_users_who_visit_city(self.city.id)
        context['number_of_visits'] = self.city.number_of_visits_all_users
        context['total_number_of_visits'] = get_total_number_of_visits()
        context = {
            **context,
            'popular_months': ', '.join(
                sorted(self.city.popular_months, key=lambda m: self.MONTH_NAMES.index(m))
            ),
            'all_cities_qty': get_number_of_cities(country_id),
            'region_cities_qty': get_number_of_cities_in_region_by_city(self.city.id),
            'visits_rank_in_country': get_rank_by_visits_of_city(
                self.city.id, self.city.country_id
            ),
            'users_rank_in_country': get_rank_by_users_of_city(self.city.id, self.city.country_id),
            'visits_rank_in_region': get_rank_by_visits_of_city_in_region(self.city.id, True),
            'users_rank_in_region': get_rank_by_users_of_city_in_region(self.city.id, True),
            'users_rank_in_country_neighboring_cities': get_neighboring_cities_by_users_rank(
                self.city.id, country_id
            ),
            'visits_rank_in_country_neighboring_cities': get_neighboring_cities_by_visits_rank(
                self.city.id, country_id
            ),
            'users_rank_neighboring_cities_in_region': (
                get_neighboring_cities_in_region_by_users_rank(self.city.id, country_id)
            ),
            'visits_rank_neighboring_cities_in_region': get_neighboring_cities_in_region_by_visits_rank(
                self.city.id, country_id
            ),
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
