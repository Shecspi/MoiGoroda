from rest_framework import generics

from country.models import Country
from country.serializer import CountrySerializer


class GetAllCountry(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    http_method_names = ['get']
