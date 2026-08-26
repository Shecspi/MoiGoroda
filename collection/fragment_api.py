# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""DMR controllers that render authenticated thematic collection fragments."""

from http import HTTPStatus

from django.http import HttpResponseBase
from dmr import Controller, ResponseSpec, validate
from dmr.plugins.msgspec import MsgspecSerializer

from city.api.visited import RequiredDjangoSessionAuth
from collection.views import (
    CollectionListFragment,
    CollectionSelectedListFragment,
    PersonalCollectionCityListFragment,
    PersonalCollectionListFragment,
)


class CollectionListFragmentController(Controller[MsgspecSerializer]):
    """Renders the query-aware thematic collection catalog through DMR."""

    auth = (RequiredDjangoSessionAuth(),)

    @validate(
        ResponseSpec(str, status_code=HTTPStatus.OK),
        validate_responses=False,
        tags=['Коллекции'],
    )
    def get(self) -> HttpResponseBase:
        return CollectionListFragment.as_view()(self.request)


class CollectionSelectedListFragmentController(Controller[MsgspecSerializer]):
    """Renders the query-aware thematic collection city list through DMR."""

    auth = (RequiredDjangoSessionAuth(),)

    @validate(
        ResponseSpec(str, status_code=HTTPStatus.OK),
        validate_responses=False,
        tags=['Коллекции'],
    )
    def get(self) -> HttpResponseBase:
        return CollectionSelectedListFragment.as_view(list_or_map='list')(
            self.request, pk=self.kwargs['pk']
        )


class PersonalCollectionListFragmentController(Controller[MsgspecSerializer]):
    """Renders the authenticated owner's personal collection catalog through DMR."""

    auth = (RequiredDjangoSessionAuth(),)

    @validate(
        ResponseSpec(str, status_code=HTTPStatus.OK),
        validate_responses=False,
        tags=['Коллекции'],
    )
    def get(self) -> HttpResponseBase:
        return PersonalCollectionListFragment.as_view()(self.request)


class PersonalCollectionCityListFragmentController(Controller[MsgspecSerializer]):
    """Renders the authenticated personal collection city list through DMR."""

    auth = (RequiredDjangoSessionAuth(),)

    @validate(
        ResponseSpec(str, status_code=HTTPStatus.OK),
        validate_responses=False,
        tags=['Коллекции'],
    )
    def get(self) -> HttpResponseBase:
        return PersonalCollectionCityListFragment.as_view()(self.request, pk=self.kwargs['pk'])
