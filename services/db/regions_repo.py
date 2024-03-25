"""
Реализует функции, взаимодействующие с моделью Region.
Любая работа с этой моделью должна происходить только через описанные в этом файле функции.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.db.models import QuerySet, Count, Q

from region.models import Region


def get_all_visited_regions(user_id: int) -> QuerySet[Region]:
    """
    Получает из базы данных все посещённые регионы пользователя с ID, указанным в user_id.
    """
    return (
        Region.objects.select_related('area')
        .annotate(
            num_total=Count('city', distinct=True),
            num_visited=Count('city', filter=Q(city__visitedcity__user_id=user_id), distinct=True),
        )
        .order_by('-num_visited', 'title')
    )
