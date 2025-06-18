from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from region.models import Region
from region.serializers import RegionSerializer


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
