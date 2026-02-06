"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import uuid
from typing import Any, cast

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import ListView

from place.models import PlaceCollection


def place(request: HttpRequest) -> HttpResponse:
    collection_uuid_raw = request.GET.get('collection', '').strip()
    collection_uuid_ctx = collection_uuid_raw
    viewing_others_collection = False
    collection_places_count = 0
    collection_title = ''

    if collection_uuid_raw:
        try:
            collection_uuid = uuid.UUID(collection_uuid_raw)
        except (ValueError, TypeError):
            raise Http404('Коллекция не найдена')
        collection = PlaceCollection.objects.filter(pk=collection_uuid).first()
        if collection is None:
            raise Http404('Коллекция не найдена')
        if not collection.is_public:
            if not request.user.is_authenticated or request.user != collection.user:
                return redirect(f'{settings.LOGIN_URL}?next={request.get_full_path()}')
        if not request.user.is_authenticated or request.user != collection.user:
            collection_title = collection.title
        if request.user.is_authenticated and request.user != collection.user:
            viewing_others_collection = True
            collection_places_count = collection.places.count()
    else:
        if not request.user.is_authenticated:
            return redirect(f'{settings.LOGIN_URL}?next={request.get_full_path()}')

    # Popup только для владельца; для гостя и не-владельца — только tooltip
    place_map_tooltip_only = bool(
        collection_uuid_ctx and (not request.user.is_authenticated or viewing_others_collection)
    )
    # Шапка: «Мои места» для владельца, иначе название коллекции (гость/не-владелец)
    is_owner_view = request.user.is_authenticated and not viewing_others_collection
    place_map_header_title = 'Мои места' if is_owner_view else (collection_title or 'Мои места')
    # Под шапкой: какая коллекция просматривается или «все коллекции»
    if collection_title:
        view_context_label = f'Коллекция: «{collection_title}»'
    elif request.user.is_authenticated:
        view_context_label = 'Все коллекции'
    else:
        view_context_label = ''

    return render(
        request,
        'place/map.html',
        context={
            'page_title': 'Мои места',
            'page_description': 'Мои места, отмеченные на карте',
            'active_page': 'places',
            'collection_uuid': collection_uuid_ctx,
            'viewing_others_collection': viewing_others_collection,
            'collection_places_count': collection_places_count,
            'collection_title': collection_title,
            'place_map_tooltip_only': place_map_tooltip_only,
            'place_map_header_title': place_map_header_title,
            'view_context_label': view_context_label,
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
