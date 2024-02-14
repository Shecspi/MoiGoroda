from django.db.models import Q, QuerySet, Count, F, FloatField
from django.db.models.functions import Cast

from region.models import Region


def get_number_of_regions() -> int:
    """
    Возвращает количество регионов, сохранённых в БД.
    """
    return Region.objects.count()


def get_number_of_visited_regions(user_id: int) -> int:
    """
    Возвращает количество посещённых регионов пользователя с ID user_id.
    """
    return (
        Region.objects
        .all()
        .exclude(visitedcity__city=None)
        .exclude(~Q(visitedcity__user__id=user_id))
        .count()
    )


def get_number_of_finished_regions(user_id: int) -> int:
    ...


def get_all_visited_regions(user_id: int) -> QuerySet:
    return (
        Region.objects
        .all()
        .annotate(
            # Добавляем в QuerySet общее количество городов в регионе
            total_cities=Count('city', distinct=True),
            # Добавляем в QuerySet количество посещённых городов в регионе
            visited_cities=Count('city', filter=Q(city__visitedcity__user__id=user_id), distinct=True),
            # Добавляем в QuerySet процентное отношение посещённых городов
            # Без Cast(..., output_field=...) деление F() на F() выдаёт int, то есть очень сильно теряется точность.
            # Например, 76 / 54 получается 1.
            ratio_visited=(
                Cast(
                    F('visited_cities'),
                    output_field=FloatField()
                ) / Cast(
                    F('total_cities'),
                    output_field=FloatField()
                )) * 100)
        .exclude(visitedcity__city=None)
        .exclude(~Q(visitedcity__user_id=user_id))
        .order_by('-ratio_visited', '-visited_cities')
    )
