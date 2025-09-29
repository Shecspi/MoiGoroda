from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from region.models import Region
from region.serializers import RegionSerializer, RegionSearchParamsSerializer


@api_view(['GET'])
def region_list_by_country(request):
    country_id = request.GET.get('country_id')
    if not country_id:
        return Response(
            {'detail': 'Параметр country_id является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    regions = Region.objects.filter(country_id=country_id).order_by('title')
    serializer = RegionSerializer(regions, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def search_region(request):
    serializer = RegionSearchParamsSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)

    query = serializer.validated_data.get('query')
    country = serializer.validated_data.get('country')

    if not query:
        return Response(
            {'detail': 'Параметр query является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    regions = Region.objects.filter(title__icontains=query).order_by('title')
    if country:
        regions = regions.filter(country__code=country)

    regions_list = [{'id': region.id, 'title': region.full_name} for region in regions]

    return Response(regions_list, status=status.HTTP_200_OK)
