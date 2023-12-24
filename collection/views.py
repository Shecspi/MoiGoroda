import logging
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q, Exists, OuterRef, Subquery, DateField, IntegerField, QuerySet, BooleanField
from django.http import Http404
from django.views.generic import ListView, DetailView

from city.models import VisitedCity, City
from collection.models import Collection
from utils.CollectionListMixin import CollectionListMixin
from utils.LoggingMixin import LoggingMixin
from utils.word_changes import change

logger = logging.getLogger('moi-goroda')


class CollectionList(CollectionListMixin, LoggingMixin, ListView):
    model = Collection
    paginate_by = 16
    template_name = 'collection/collection__list.html'

    def __init__(self):
        super().__init__()

        # Список ID городов из таблицы City, которые посещены пользователем
        self.visited_cities = None
        self.sort: str = ''
        self.filter: str = ''
        self.qty_of_collections: int = 0
        self.qty_of_started_colelctions: int = 0
        self.qty_of_finished_colelctions: int = 0

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Collection.objects.prefetch_related('city').annotate(
                qty_of_cities=Count('city', distinct=True),
                qty_of_visited_cities=Count('city__visitedcity', filter=Q(city__visitedcity__user=self.request.user))
            )

            self.visited_cities = VisitedCity.objects.filter(
                user=self.request.user
            ).values_list('city__id', flat=True)
        else:
            queryset = Collection.objects.prefetch_related('city').annotate(
                qty_of_cities=Count('city', distinct=True)
            )

        self.set_message(self.request, f'Viewing the collection list')

        # Обновление счётчиков коллекций
        self.qty_of_collections = queryset.count()
        if self.request.user.is_authenticated:
            for collection in queryset:
                if collection.qty_of_visited_cities > 0:
                    self.qty_of_started_colelctions += 1
                if collection.qty_of_visited_cities == collection.qty_of_cities:
                    self.qty_of_finished_colelctions += 1

        # Фильтры работают только для авторизованного пользователя
        if self.request.GET.get('filter') and self.request.user.is_authenticated:
            self.filter = self.request.GET.get('filter')
            try:
                queryset = self.apply_filter_to_queryset(queryset, self.filter)
                self.set_message(self.request, f'Using filtering \'{self.filter}\'')
            except KeyError:
                self.set_message(
                    self.request,
                    f"Unexpected value of the GET-param 'filter' - {self.request.GET.get('filter')}"
                )
                self.filter = ''

        # Определяем сортировку
        sort_default = 'default_auth' if self.request.user.is_authenticated else 'default_guest'
        self.sort = self.request.GET.get('sort') if self.request.GET.get('sort') else sort_default
        try:
            queryset = self.apply_sort_to_queryset(queryset, self.sort)
            if self.sort != 'default_auth' and self.sort != 'default_guest':
                self.set_message(self.request, f'Using sorting \'{self.sort}\'')
        except KeyError:
            self.set_message(
                self.request,
                f"Unexpected value of the GET-param 'sort' - {self.sort}"
            )
            queryset = self.apply_sort_to_queryset(queryset, sort_default)
            self.sort = ''

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sort'] = self.sort
        context['filter'] = self.filter
        context['visited_cities'] = self.visited_cities  # Все коллекции, в которых находится город
        context['qty_of_collections'] = self.qty_of_collections
        context['qty_of_started_colelctions'] = self.qty_of_started_colelctions
        context['qty_of_finished_colelctions'] = self.qty_of_finished_colelctions

        context['active_page'] = 'collection'

        url_params_for_sort = '' if self.sort == 'default_auth' or self.sort == 'default_guest' else self.sort

        context['url_for_filter_not_started'] = self.get_url_params(
            'not_started' if self.filter != 'not_started' else '',
            url_params_for_sort
        )
        context['url_for_filter_finished'] = self.get_url_params(
            'finished' if self.filter != 'finished' else '',
            url_params_for_sort
        )
        context['url_for_sort_name_down'] = self.get_url_params(self.filter, 'name_down')
        context['url_for_sort_name_up'] = self.get_url_params(self.filter, 'name_up')
        context['url_for_sort_progress_down'] = self.get_url_params(self.filter, 'progress_down')
        context['url_for_sort_progress_up'] = self.get_url_params(self.filter, 'progress_up')

        context['page_title'] = 'Коллекции городов'
        context['page_description'] = 'Города России, распределённые по различным коллекциям. Путешествуйте по России и закрывайте коллекции.'

        return context


class CollectionSelected_List(LoggingMixin, ListView):
    model = Collection
    paginate_by = 16

    list_or_map: str = 'list'

    def __init__(self, list_or_map: str):
        super().__init__()

        self.qty_of_visited_cities = None
        self.qty_of_cities = None
        self.pk = None
        self.filter = ''
        self.cities = None
        self.collection_title = ''
        self.list_or_map = list_or_map

    def get(self, *args: Any, **kwargs: Any):
        self.pk = self.kwargs['pk']

        # При обращении к несуществующей коллекции выдаём 404
        # При этом в указанной коллекции может не быть посещённых городов, это ок
        try:
            self.collection_title = Collection.objects.get(id=self.pk)
        except ObjectDoesNotExist as exc:
            self.set_message(self.request, 'Attempt to access a non-existent region')
            raise Http404 from exc

        return super().get(*args, **kwargs)

    def get_queryset(self):
        """
        Получает из базы данных все города коллекции, как посещённые так и нет,
        и возвращает Queryset, состоящий из полей:
            * `id` - ID города
            * `title` - название города
            * `population` - население города
            * `date_of_foundation` - дата основания города
            * `coordinate_width` - широта
            * `coordinate_longitude` - долгота
            * `is_visited` - True,если город посещён

            Для авторизованных пользователей доступны дополнительные поля:
            * `visited_id` - ID посещённого города
            * `date_of_visit` - дата посещения
            * `has_magnet` - True, если имеется магнит
            * `rating` - рейтинг от 1 до 5
        """
        # В связи с тем, что модель Collections - это связь Many To Many, я не нашёл способа,
        # как из неё получить список городов и иметь возможность аннотировать этот список дополнительными полями.
        # Поэтому я вручную выбираю из таблицы City все города, находящиеся в указанной коллекции,
        # и уже их аннотирую доп. полями.
        # Но для этого нужен список ID городов, которые есть в коллекции. Для этого и создаётся следующая переменная.
        cities_id = [city.id for city in Collection.objects.get(id=self.pk).city.all()]

        self.cities = City.objects.filter(id__in=cities_id).annotate(
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
            'id', 'title', 'is_visited', 'population', 'date_of_foundation',
            'coordinate_width', 'coordinate_longitude',
            'visited_id', 'date_of_visit', 'has_magnet', 'rating'
        )

        self.qty_of_cities = len(self.cities)
        self.qty_of_visited_cities = sum([1 if city['is_visited'] else 0 for city in self.cities])

        # Определяем фильтрацию
        if self.request.user.is_authenticated:
            self.filter = self.request.GET.get('filter') if self.request.GET.get('filter') else ''
            if self.filter:
                try:
                    self.cities = apply_filter(self.cities, self.filter)
                    self.set_message(self.request, f'Using filtering \'{self.filter}\'')
                except KeyError:
                    self.set_message(self.request, f'Unexpected value of the GET-argument \'filter={self.filter}\'')

        return self.cities

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['filter'] = self.filter

        context['qty_of_cities'] = self.qty_of_cities
        context['qty_of_visited_cities'] = self.qty_of_visited_cities
        context['cities'] = self.cities

        context['change__city'] = change('город', self.qty_of_visited_cities)
        context['change__visited'] = change('посещено', self.qty_of_visited_cities)

        context['url_for_filter_visited'] = get_url_params('visited' if self.filter != 'visited' else '')
        context['url_for_filter_not_visited'] = get_url_params('not_visited' if self.filter != 'not_visited' else '')

        context['pk'] = self.pk
        context['page_title'] = self.collection_title
        context['page_description'] = (f'Города России, представленные в коллекции "{self.collection_title}". '
                                       f'Путешествуйте по России и закрывайте коллекции.')

        return context

    def get_template_names(self) -> list[str]:
        if self.list_or_map == 'list':
            return ['collection/collection_selected__list.html', ]
        elif self.list_or_map == 'map':
            return ['collection/collection_selected__map.html', ]


def apply_filter(queryset: QuerySet, filter_value: str) -> QuerySet:
    """
    Производит фильтрацию 'queryset' на основе значения 'filter'.

    @param queryset: QuerySet, к которому необходимо применить фильтр.
    @param filter_value: Параметр, на основе которого производится фильтрация.
        Может принимать одно из 2 значение:
            - 'not_started' - коллекции, в которых нет ни одного опсещённого города;
            - 'finished' - коллекции, в которых посещены все города.
    @return: Отфильтрованный QuerySet или KeyError, если передан некорректный параметр `filter_value`.
    """
    match filter_value:
        case 'visited':
            queryset = queryset.filter(is_visited=True)
        case 'not_visited':
            queryset = queryset.filter(is_visited=False)
        case _:
            raise KeyError

    return queryset


def get_url_params(filter_value: str | None) -> str | None:
    """
    Возвращает строку, пригодную для использования в URL-адресе после знака '?' с параметрами 'filter' и 'sort'
    @param filter_value: Значение фльтра, может быть пустой строкой.
    """
    valid_filters = ['visited', 'not_visited']
    print(filter_value, valid_filters, filter_value in valid_filters)

    if filter_value and filter_value in valid_filters:
        return f'filter={filter_value}'

    return ''
