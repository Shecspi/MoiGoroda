import logging

from django.db.models import Count, Q
from django.views.generic import ListView

from city.models import VisitedCity
from collection.models import Collection
from utils.CollectionListMixin import CollectionListMixin


logger = logging.getLogger('moi-goroda')


class CollectionList(CollectionListMixin, ListView):
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
            except KeyError:
                logger.warning(f"Unexpected value of the GET-param 'filter' - {self.request.GET.get('filter')}")
                self.filter = ''

        # Определяем сортировку
        sort_default = 'default_auth' if self.request.user.is_authenticated else 'default_guest'
        self.sort = self.request.GET.get('sort') if self.request.GET.get('sort') else sort_default
        try:
            queryset = self.apply_sort_to_queryset(queryset, self.sort)
        except KeyError:
            logger.warning(f"Unexpected value of the GET-param 'sort' - {self.sort}")
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

        return context