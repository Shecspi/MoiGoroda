from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from region.models import Region
from region.serializers import RegionSerializer, RegionSearchParamsSerializer


@api_view(['GET'])
def region_list_by_country(request: Request) -> Response:
    """
    Возвращает список регионов для одной или нескольких стран.

    Принимает параметр country_id (один ID) или country_ids (несколько ID через запятую).
    Если передан country_id, используется он. Если передан country_ids, используется он.
    Если передан и country_id, и country_ids, приоритет у country_ids.

    :param request: DRF Request
    :return: Response со списком регионов
    """
    country_ids_param = request.GET.get('country_ids')
    country_id_param = request.GET.get('country_id')

    if not country_ids_param and not country_id_param:
        return Response(
            {'detail': 'Параметр country_id или country_ids является обязательным'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Если передан country_ids, используем его (приоритет)
    if country_ids_param:
        try:
            country_ids = [int(id.strip()) for id in country_ids_param.split(',') if id.strip()]
        except ValueError:
            return Response(
                {
                    'detail': 'Параметр country_ids должен содержать список числовых ID через запятую'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        # Используем country_id (обратная совместимость)
        if country_id_param is None:
            return Response(
                {'detail': 'Параметр country_id является обязательным'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            country_ids = [int(country_id_param)]
        except ValueError:
            return Response(
                {'detail': 'Параметр country_id должен быть числом'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    if not country_ids:
        return Response(
            {'detail': 'Не указаны валидные ID стран'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    regions = (
        Region.objects.filter(country_id__in=country_ids)
        .select_related('country')
        .order_by('full_name')
    )
    serializer = RegionSerializer(regions, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def search_region(request: Request) -> Response:
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
