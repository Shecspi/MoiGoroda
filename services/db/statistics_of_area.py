from django.db.models import Count, F, FloatField, Q, QuerySet
from django.db.models.functions import Cast

from region.models import Area


def get_visited_areas(user_id: int) -> QuerySet:
    return (
        Area.objects
        .all()
        .annotate(
            # Добавляем в QuerySet общее количество регионов в округе
            total_regions=Count('region', distinct=True),
            # Добавляем в QuerySet количество посещённых регионов в округе
            visited_regions=Count('region', filter=Q(region__visitedcity__user__id=user_id), distinct=True),
            # Добавляем в QuerySet процентное соотношение посещённых регионов.
            # Без Cast(..., output_field=...) деление F() на F() выдаёт int, то есть очень сильно теряется точность.
            # Например, 76 / 54 получается 1.
            ratio_visited=(
                Cast(
                    F('visited_regions'), output_field=FloatField()
                ) / Cast(
                    F('total_regions'), output_field=FloatField()
                )
            ) * 100)
        .order_by('-ratio_visited', 'title')
    )
