from datetime import datetime, timedelta, timezone
from typing import Any

from django.db.models import Count, Max, Func, F, Value
from django.db.models.fields import CharField
from django.db.models.functions.datetime import TruncDay, TruncDate
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from country.models import VisitedCountry


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
