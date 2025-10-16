"""
Реализует функции, работающие с моделью Area.
----------------------------------------------

Copyright 2024 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django.db.models import Count, F, FloatField, Q, QuerySet
from django.db.models.functions import Cast

from region.models import Area


def get_visited_areas(user_id: int) -> QuerySet[Any, Any]:
    """
    Возвращает последовательность федеральных округов из БД, которая имеет дополнительные поля:
     - total_regions: количество регионов в федеральном округе;
     - visited_regions: количество посещённых регионов в федеральном округе;
     - ratio_visited: процентное соотношение количества посещённых регионов к общему количеству.

     Записи сортируются сначала по полю ratio_visited (от большего к меньшему), а потом по полю title.
    """
    return (
        Area.objects.all()
        .annotate(
            # Добавляем в QuerySet общее количество регионов в округе
            total_regions=Count('region', distinct=True),
            # Добавляем в QuerySet количество посещённых регионов в округе
            visited_regions=Count(
                'region', filter=Q(region__city__visitedcity__user__id=user_id), distinct=True
            ),
            # Добавляем в QuerySet процентное соотношение посещённых регионов.
            # Без Cast(..., output_field=...) деление F() на F() выдаёт int, то есть очень сильно теряется точность.
            # Например, 76 / 54 получается 1.
            ratio_visited=(
                Cast(F('visited_regions'), output_field=FloatField())
                / Cast(F('total_regions'), output_field=FloatField())
            )
            * 100,
        )
        .order_by('-ratio_visited', 'title')
    )
