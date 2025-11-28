"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import date, datetime, timedelta, timezone
from http import HTTPStatus
from typing import Any

import msgspec
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, F, Func, Max, Value
from django.db.models.fields import CharField
from django.db.models.functions.datetime import TruncDate, TruncDay
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from country.models import VisitedCountry
from django_modern_rest import Controller
from django_modern_rest.decorators import wrap_middleware
from django_modern_rest.plugins.msgspec import MsgspecSerializer
from django_modern_rest.response import ResponseSpec, build_response
from MoiGoroda.settings import Error


class QuantityModel(msgspec.Struct):
    quantity: int


@wrap_middleware(
    user_passes_test(lambda user: user.is_superuser),
    ResponseSpec(
        return_type=dict[str, str],
        status_code=HTTPStatus.FOUND,
    ),
)
def is_superuser_json(response: HttpResponse) -> HttpResponse:
    """
    Декоратор, который оборачивает представление для проверки прав доступа пользователя.
    Если попытка доступа осуществляется не привилегированным пользователем и возвращается статус 302 (FOUND),
    декоратор преобразует ответ в JSON с кодом 401 (UNAUTHORIZED) и сообщением о том, что доступ разрешён
    только администраторам.

    Аргументы:
        response (HttpResponse): HTTP-ответ, который необходимо обработать.

    Возвращает:
        HttpResponse: Оригинальный ответ, если редирект не требуется,
        либо JSON-ответ с ошибкой, если пользователь не имеет прав администратора.
    """
    if response.status_code == HTTPStatus.FOUND:
        return build_response(
            MsgspecSerializer,
            raw_data={'detail': 'Access restricted to administrators only.'},
            status_code=HTTPStatus.UNAUTHORIZED,
        )

    return response


@is_superuser_json
class GetNumberOfUsersController(Controller[MsgspecSerializer]):
    def get(self) -> QuantityModel:
        number_of_users = User.objects.count()
        return QuantityModel(quantity=number_of_users)


@is_superuser_json
class GetNumberOfRegistrationsYesterdayController(Controller[MsgspecSerializer]):
    def get(self) -> QuantityModel:
        qty = User.objects.filter(date_joined__date=date.today() - timedelta(days=1)).count()
        return QuantityModel(quantity=qty)


@is_superuser_json
class GetNumberOfRegistrationsWeekController(Controller[MsgspecSerializer]):
    def get(self) -> QuantityModel:
        qty = (
            User.objects.annotate(day=TruncDay('date_joined', tzinfo=timezone.utc))
            .filter(day__range=[date.today() - timedelta(days=7), date.today() - timedelta(days=1)])
            .count()
        )
        return QuantityModel(quantity=qty)


@is_superuser_json
class GetNumberOfRegistrationsMonthController(Controller[MsgspecSerializer]):
    def get(self) -> QuantityModel:
        qty = (
            User.objects.annotate(day=TruncDay('date_joined', tzinfo=timezone.utc))
            .filter(
                day__range=[date.today() - timedelta(days=30), date.today() - timedelta(days=1)]
            )
            .count()
        )
        return QuantityModel(quantity=qty)


class GetTotalVisitedCountries(generics.ListAPIView):  # type: ignore[type-arg]
    queryset = VisitedCountry.objects.all()  # type: ignore[assignment]
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response({'qty': VisitedCountry.objects.count()})


class GetUsersWithVisitedCountries(generics.ListAPIView):  # type: ignore[type-arg]
    queryset = VisitedCountry.objects.all()  # type: ignore[assignment]
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response({'qty': self.queryset.values('user').distinct().count()})


class GetAverageQtyVisitedCountries(generics.ListAPIView):  # type: ignore[type-arg]
    queryset = VisitedCountry.objects.all()  # type: ignore[assignment]
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        total_visited_countries = self.queryset.count()
        total_users = self.queryset.values('user').distinct().count()

        if total_users == 0:
            return Response({'qty': 0})

        return Response({'qty': int(total_visited_countries / total_users)})


class GetMaxQtyVisitedCountries(generics.ListAPIView):  # type: ignore[type-arg]
    queryset = VisitedCountry.objects.all()  # type: ignore[assignment]
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        max_qty = (
            self.queryset.values('user')
            .annotate(Count('country'))
            .aggregate(qty=Max('country__count'))
        )

        return Response(max_qty)


class GetAddedVisitedCountryYeterday(generics.ListAPIView):  # type: ignore[type-arg]
    queryset = VisitedCountry.objects.all()  # type: ignore[assignment]
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        days: int = self.kwargs['days']
        start_date = datetime.now().date() - timedelta(days=days)
        finish_date = datetime.now().date() + timedelta(days=1)
        queryset = self.queryset.filter(added_at__range=[start_date, finish_date])

        return Response({'qty': queryset.count()})


class GetAddedVisitedCountriesByDay(generics.ListAPIView):  # type: ignore[type-arg]
    queryset = VisitedCountry.objects.all()  # type: ignore[assignment]
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = (
            self.queryset.annotate(day=TruncDay('added_at', tzinfo=timezone.utc))
            .order_by('day')
            .annotate(
                # Форматирование даты в формат DD-MM-YYYY
                date=Func(
                    TruncDate(F('day')),
                    Value('DD.MM.YYYY'),
                    function='to_char',
                    output_field=CharField(),
                )
            )
            .values('date')
            .annotate(qty=Count('id'))[:50]
        )

        return Response(list(queryset))
