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
