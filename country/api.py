from rest_framework import generics
import rest_framework.exceptions as drf_exc
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from country.models import Country, VisitedCountry
from country.serializer import CountrySerializer, VisitedCountrySerializer
from services import logger


class GetAllCountry(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]


class GetVisitedCountry(generics.ListAPIView):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    serializer_class = VisitedCountrySerializer

    def get_queryset(self):
        return VisitedCountry.objects.filter(user=self.request.user)


class AddVisitedCountry(generics.CreateAPIView):
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]
    serializer_class = VisitedCountrySerializer

    def post(self, request, *args, **kwargs):
        from_page = request.data.get('from') if request.data.get('from') else 'unknown location'

        serializer = VisitedCountrySerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            logger.warning(
                self.request,
                f'(API: Add visited country) Validation in the serializer failed from {from_page}. {serializer.errors}',
            )
            raise drf_exc.ValidationError(serializer.errors)

        serializer.save(user=request.user)

        return Response({'status': 'success', 'country': serializer.data})


class DeleteVisitedCountry(generics.DestroyAPIView):
    pass
