from datetime import datetime, timedelta

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
