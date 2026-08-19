# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""DMR controllers that render authenticated thematic collection fragments."""

from http import HTTPStatus

from django.http import HttpResponse
from dmr import Controller, ResponseSpec, validate
from dmr.plugins.msgspec import MsgspecSerializer

from city.api.visited import RequiredDjangoSessionAuth
from collection.views import CollectionListFragment, CollectionSelectedListFragment


class CollectionListFragmentController(Controller[MsgspecSerializer]):
    """Renders the query-aware thematic collection catalog through DMR."""

    auth = (RequiredDjangoSessionAuth(),)

    @validate(
        ResponseSpec(str, status_code=HTTPStatus.OK),
        validate_responses=False,
        tags=['Коллекции'],
    )
    def get(self) -> HttpResponse:
        return CollectionListFragment.as_view()(self.request)


class CollectionSelectedListFragmentController(Controller[MsgspecSerializer]):
    """Renders the query-aware thematic collection city list through DMR."""

    auth = (RequiredDjangoSessionAuth(),)

    @validate(
        ResponseSpec(str, status_code=HTTPStatus.OK),
        validate_responses=False,
        tags=['Коллекции'],
    )
    def get(self) -> HttpResponse:
        return CollectionSelectedListFragment.as_view(list_or_map='list')(
            self.request, pk=self.kwargs['pk']
        )
