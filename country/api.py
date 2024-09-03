from rest_framework import generics
import rest_framework.exceptions as drf_exc
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from country.models import Country, VisitedCountry
from country.serializer import CountrySerializer, VisitedCountrySerializer
from services import logger


class GetAllCountry(generics.ListAPIView):
    queryset = Country.objects.all()
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    serializer_class = CountrySerializer

    def get(self, *args, **kwargs):
        from_page = (
            self.request.GET.get('from') if self.request.GET.get('from') else 'unknown location'
        )

        logger.info(
            self.request,
            f'(API: Country): Successful request for a list of all countries from {from_page}',
        )
        return super().get(self, *args, **kwargs)


class GetVisitedCountry(generics.ListAPIView):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    serializer_class = VisitedCountrySerializer

    def get(self, *args, **kwargs):
        from_page = (
            self.request.GET.get('from') if self.request.GET.get('from') else 'unknown location'
        )

        logger.info(
            self.request,
            f'(API: Country): Successful request for a list of visited countries from {from_page}',
        )
        return super().get(self, *args, **kwargs)

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

        logger.info(
            self.request,
            f'(API: Country): The visited country has been successfully added from {from_page}',
        )

        return Response({'status': 'success', 'country': serializer.data})


class DeleteVisitedCountry(generics.DestroyAPIView):
    http_method_names = ['delete']
    permission_classes = [IsAuthenticated]
    serializer_class = VisitedCountrySerializer

    def delete(self, request, *args, **kwargs):
        from_page = request.data.get('from') if request.data.get('from') else 'unknown location'
        code = kwargs.get('code').upper()

        try:
            country = Country.objects.get(code=code)
        except Country.DoesNotExist:
            logger.warning(
                self.request,
                f"(API: Country): Country with code '{code}' not found from {from_page}",
            )
            raise drf_exc.NotFound(f"Country with code '{code}' not found")

        # В таблице VisitedCountry не должно быть больше одного элемента
        # с одинаковыми полями user и country, поэтому дополнительную проверку на это можно не делать.
        visited_country = VisitedCountry.objects.filter(user=request.user, country=country)

        # delete() к несуществующей записи не создаёт исключений, поэтому обработка исключений не требуется
        visited_country.delete()

        logger.info(
            self.request,
            f'(API: Country): The visited country has been successfully deleted from {from_page}',
        )

        return Response(status=204)
