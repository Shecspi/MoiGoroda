# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""DMR controllers that render authenticated region list HTML fragments."""

from http import HTTPStatus

from django.http import HttpResponse
from dmr import Controller, ResponseSpec, validate
from dmr.plugins.msgspec import MsgspecSerializer

from city.api.visited import RequiredDjangoSessionAuth
from region.views import CitiesByRegionListFragment, RegionListFragment


class RegionListFragmentController(Controller[MsgspecSerializer]):
    """Renders the query-aware country region list fragment through DMR."""

    auth = (RequiredDjangoSessionAuth(),)

    @validate(
        ResponseSpec(str, status_code=HTTPStatus.OK),
        validate_responses=False,
        tags=['Регионы'],
    )
    def get(self) -> HttpResponse:
        return RegionListFragment.as_view(list_or_map='list')(self.request)


class CitiesByRegionListFragmentController(Controller[MsgspecSerializer]):
    """Renders the query-aware selected region city list fragment through DMR."""

    auth = (RequiredDjangoSessionAuth(),)

    @validate(
        ResponseSpec(str, status_code=HTTPStatus.OK),
        validate_responses=False,
        tags=['Регионы'],
    )
    def get(self) -> HttpResponse:
        return CitiesByRegionListFragment.as_view(list_or_map='list')(
            self.request, pk=self.kwargs['pk']
        )
