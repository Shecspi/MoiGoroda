from typing import Any

from django.db.models import QuerySet, OuterRef, Exists, Count, Subquery, Q, Sum
from django.views.generic import ListView

from city.models import City, VisitedCity
from collection.models import Collection


class CollectionList(ListView):
    model = Collection
    paginate_by = 16
    template_name = 'collection/collection__list.html'

    def __init__(self):
        super().__init__()
        self.visited_cities = None

    def get_queryset(self) -> QuerySet[dict]:
        queryset = Collection.objects.prefetch_related('city').annotate(
            qty_of_cities=Count('city', distinct=True),
            qty_of_visited_cities=Count('city__visitedcity', filter=Q(city__visitedcity__user=self.request.user))
        )

        # Список ID посещённых городов
        self.visited_cities = VisitedCity.objects.filter(
            user=self.request.user
        ).values_list('city_id', flat=True)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        # Все коллекции, в которых находится город
        context['alone_city'] = City.objects.get(id=40)
        context['collection_list'] = context['alone_city'].collections_list.all()
        context['visited_cities'] = self.visited_cities

        return context
