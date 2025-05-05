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
from django.shortcuts import render
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
from city.sort import apply_sort_to_queryset
from city.filter import apply_filter_to_queryset
from collection.models import Collection
from services import logger
from services.db.city_repo import get_number_of_cities
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

    def get_initial(self) -> dict[str, Any]:
        """
        В случае, когда в URL передан city_id, необходимо определить город и автоматически выбрать его в форме
        """
        initial = super().get_initial()

        city_id = self.request.GET.get('city_id')
        if city_id:
            try:
                city_id = int(city_id)
                if City.objects.filter(id=city_id).exists():
                    initial['city'] = city_id
                else:
                    logger.warning(
                        self.request, f'(Visited city) City with id={city_id} does not exist'
                    )
            except (ValueError, TypeError):
                logger.warning(self.request, f'(Visited city) Invalid city_id passed: {city_id}')
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

        # Проверяем, есть ли записи с таким же user_id и city_id.
        # Если есть, то поле is_first_visit должно быть False, иначе True.
        city = form.cleaned_data.get('city')
        user = self.request.user
        is_first_visit = not VisitedCity.objects.filter(user=user, city=city).exists()
        form.instance.is_first_visit = is_first_visit

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
        return reverse('city-selected', kwargs={'pk': self.object.city.id})

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        return super().form_valid(form)

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
            self.city.visits = VisitedCity.objects.filter(
                user=self.request.user, city=self.city
            ).values('id', 'date_of_visit', 'rating', 'impression', 'city__title')

        self.city.collections = Collection.objects.filter(city=self.city)

        logger.info(self.request, f'(Visited city) Viewing the visited city #{self.city.pk}')
        return self.city

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['page_title'] = self.city.title
        context['page_description'] = f'Информация про посещённый город - {self.city.title}'

        return context


class VisitedCity_Map(LoginRequiredMixin, TemplateView):
    template_name = 'city/city_all__map.html'

    def get_context_data(
        self, *, object_list: QuerySet[dict] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        logger.info(self.request, '(Visited city) Viewing the map of visited cities')

        user_id = self.request.user.pk

        number_of_cities = get_number_of_cities()
        number_of_visited_cities = get_number_of_visited_cities(user_id)

        context['total_qty_of_cities'] = number_of_cities
        context['qty_of_visited_cities'] = number_of_visited_cities

        context['declension_of_total_cities'] = modification__city(number_of_cities)
        context['declension_of_visited_cities'] = modification__city(number_of_visited_cities)
        context['declension_of_visited'] = modification__visited(number_of_visited_cities)

        context['active_page'] = 'city_map'

        context['is_user_has_subscriptions'] = is_user_has_subscriptions(user_id)
        context['subscriptions'] = get_all_subscriptions(user_id)

        context['page_title'] = 'Карта посещённых городов'
        context['page_description'] = 'Карта с отмеченными посещёнными городами'

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
    template_name = 'city/city_all__list.html'

    all_cities = None

    def __init__(self) -> None:
        super().__init__()

        self.sort: str | None = ''
        self.filter: str | None = ''
        self.user_id: int | None = None
        self.total_qty_of_cities: int = 0
        self.qty_of_visited_cities: int = 0
        self.has_subscriptions: bool = False
        self.qty_of_visited_cities_last_year: int = 0
        self.qty_of_visited_cities_current_year: int = 0
        self.all_visited_cities: QuerySet[VisitedCity] | None = None

    def get_queryset(self) -> QuerySet[VisitedCity]:
        self.user_id = self.request.user.pk
        self.filter = self.request.GET.get('filter')

        self.queryset = get_all_visited_cities(self.user_id)
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

        context['active_page'] = 'city_list'
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
        context['url_for_sort_date_down'] = self.get_url_params(
            self.filter, 'first_visit_date_down'
        )
        context['url_for_sort_date_up'] = self.get_url_params(self.filter, 'first_visit_date_up')
        context['url_for_sort_last_date_down'] = self.get_url_params(
            self.filter, 'last_visit_date_down'
        )
        context['url_for_sort_last_date_up'] = self.get_url_params(
            self.filter, 'last_visit_date_up'
        )

        context['is_user_has_subscriptions'] = is_user_has_subscriptions(self.user_id)
        context['subscriptions'] = get_all_subscriptions(self.user_id)

        context['page_title'] = 'Список посещённых городов'
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
