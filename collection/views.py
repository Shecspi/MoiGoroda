from django.views.generic import ListView

from city.models import City
from collection.models import Collection


class CollectionList(ListView):
    model = Collection
    template_name = 'collection/collection__list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['alone_city'] = City.objects.get(id=40)
        context['collection_list'] = context['alone_city'].collections_list.all()

        return context
