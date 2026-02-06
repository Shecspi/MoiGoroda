"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

from typing import Any, cast

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView

from place.models import PlaceCollection


@login_required
def place(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'place/map.html',
        context={
            'page_title': 'Мои места',
            'page_description': 'Мои места, отмеченные на карте',
            'active_page': 'places',
            'collection_uuid': request.GET.get('collection', ''),
        },
    )


class PlaceCollectionsListView(LoginRequiredMixin, ListView):  # type: ignore[type-arg]
    """Список коллекций мест пользователя (карточки как на /collection/personal)."""

    model = PlaceCollection
    paginate_by = 16
    template_name = 'place/collections/page.html'
    context_object_name = 'collection_list'

    def get_queryset(self) -> Any:
        user = cast(User, self.request.user)
        return (
            PlaceCollection.objects.filter(user=user)
            .annotate(places_count=Count('places'))
            .order_by('-updated_at')
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'places'
        context['page_title'] = 'Коллекции мест'
        context['page_description'] = (
            'Ваши коллекции мест. Нажмите на название — откроется карта с фильтром по этой коллекции.'
        )
        return context
