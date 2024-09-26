from datetime import datetime, timedelta, timezone

from django.db.models import Count, Max, Func, F, Value
from django.db.models.fields import CharField
from django.db.models.functions.datetime import TruncDay, TruncDate
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from country.models import VisitedCountry


class GetTotalVisitedCountries(generics.ListAPIView):
    queryset = VisitedCountry.objects.all()
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        return Response({'qty': VisitedCountry.objects.count()})


class GetUsersWithVisitedCountries(generics.ListAPIView):
    queryset = VisitedCountry.objects.all()
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        return Response({'qty': self.queryset.values('user').distinct().count()})


class GetAverageQtyVisitedCountries(generics.ListAPIView):
    queryset = VisitedCountry.objects.all()
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        total_visited_countries = self.queryset.count()
        total_users = self.queryset.values('user').distinct().count()

        return Response({'qty': int(total_visited_countries / total_users)})


class GetMaxQtyVisitedCountries(generics.ListAPIView):
    queryset = VisitedCountry.objects.all()
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        max_qty = (
            self.queryset.values('user')
            .annotate(Count('country'))
            .aggregate(qty=Max('country__count'))
        )

        return Response(max_qty)


class GetAddedVisitedCountryYeterday(generics.ListAPIView):
    queryset = VisitedCountry.objects.all()
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        days = self.kwargs['days']
        start_date = datetime.now().date() - timedelta(days=days)
        finish_date = datetime.now().date() + timedelta(days=1)
        queryset = self.queryset.filter(added_at__range=[start_date, finish_date])

        return Response({'qty': queryset.count()})


class GetAddedVisitedCountriesByDay(generics.ListAPIView):
    queryset = VisitedCountry.objects.all()
    http_method_names = ['get']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        queryset = (
            self.queryset.annotate(day=TruncDay('added_at', tzinfo=timezone.utc))
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
            .annotate(qty=Count('id'))
            .order_by('date')[:50]
        )

        return Response(list(queryset))
