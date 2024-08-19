from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from country.models import Country
from country.serializer import CountrySerializer


class GetAllCountry(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]


class GetVisitedCountry(generics.ListAPIView):
    pass


class AddVisitedCountry(generics.CreateAPIView):
    pass


class DeleteVisitedCountry(generics.DestroyAPIView):
    pass
