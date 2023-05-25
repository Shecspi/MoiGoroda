from django.views.generic import ListView

from collection.models import Collection


class CollectionList(ListView):
    model = Collection
    template_name = 'collection/collection__list.html'
