# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

"""DMR controllers that render authenticated list HTML fragments."""

from http import HTTPStatus

from django.http import HttpResponse
from dmr import Controller, ResponseSpec, validate
from dmr.plugins.msgspec import MsgspecSerializer

from city.api.visited import RequiredDjangoSessionAuth
from city.views import VisitedCityListFragment, VisitedCityVisitsFragment


class VisitedCityListFragmentController(Controller[MsgspecSerializer]):
    """Renders the existing query-aware city list fragment through DMR."""

    auth = (RequiredDjangoSessionAuth(),)

    @validate(
        ResponseSpec(str, status_code=HTTPStatus.OK),
        validate_responses=False,
        tags=['Посещённые города'],
    )
    def get(self) -> HttpResponse:
        return VisitedCityListFragment.as_view()(self.request)


class VisitedCityVisitsFragmentController(Controller[MsgspecSerializer]):
    """Renders the authenticated visits surface for one city detail page."""

    auth = (RequiredDjangoSessionAuth(),)

    @validate(
        ResponseSpec(str, status_code=HTTPStatus.OK),
        validate_responses=False,
        tags=['Посещённые города'],
    )
    def get(self) -> HttpResponse:
        return VisitedCityVisitsFragment.as_view()(self.request, pk=self.kwargs['pk'])
