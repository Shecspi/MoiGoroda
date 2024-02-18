"""
Реализует функцию, генерирующую поддельные данные для страницы статистики.
----------------------------------------------

Copyright 2024 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""


import datetime
import calendar

from django.db.models import F, QuerySet, Count
from django.db.models.functions import TruncYear, TruncMonth

from city.models import VisitedCity, City


def get_number_of_cities() -> int:
    """
    Возвращает общее количество городов в России.
    """
    return City.objects.count()


def get_number_of_visited_cities(user_id: int) -> int:
    """
    Возвращает количество посещённых городов пользователем с ID, указанном в user_id.
    """
    return VisitedCity.objects.filter(user=user_id).count()


def get_number_of_not_visited_cities(user_id: int) -> int:
    """
    Возвращает количество непосещённых городов пользователем с ID, указанном в user_id.
    """
    return City.objects.count() - VisitedCity.objects.filter(user=user_id).count()


def get_number_of_visited_cities_by_year(user_id: int, year: int) -> int:
    """
    Возвращает количество посещённых городов пользователем с ID, указанном в user_id, за один год, указанный в year.
    """
    return VisitedCity.objects.filter(user=user_id, date_of_visit__year=year).count()


def get_number_of_visited_cities_in_several_years(user_id: int):
    """
    Возвращает статистику по количеству посещённых городов за каждый год.
    """
    return (VisitedCity.objects.filter(user=user_id)
            .annotate(year=TruncYear('date_of_visit'))
            .values('year')
            .exclude(year=None)
            .annotate(qty=Count('id', distinct=True))
            .values('year', 'qty'))


def get_number_of_visited_cities_in_several_month(user_id: int):
    """
    Возвращает статистику по количеству посещённых городов за каждый месяц (последние 24 месяца).
    """

    # В график идут последние 24 месяца, для этого вычисляется месяц отсчёта и месяц завершения графика.
    # Для того чтобы первый и последний месяцы полностью попали в расчёт, нужно в первом месяце
    # указать началом 1 день, а в последнем - последний.
    now = datetime.datetime.now()
    start_date = datetime.date(now.year - 2, now.month + 1, 1)
    last_day_of_end_month = calendar.monthrange(now.year, now.month)[1]
    end_date = datetime.date(now.year, now.month, last_day_of_end_month)

    result = (
        VisitedCity.objects.filter(user=user_id)
        .filter(date_of_visit__range=(start_date, end_date))
        .annotate(month_year=TruncMonth('date_of_visit'))
        .values('month_year')
        .order_by('-month_year')
        .exclude(month_year=None)
        .annotate(qty=Count('id', distinct=True))
        .values('month_year', 'qty')
    )

    return result


def get_last_10_visited_cities(user_id: int) -> QuerySet:
    """
    Возвращает последние 10 посещённых городов пользователя с ID, указанным в user_id.
    """
    return (
        VisitedCity.objects
        .filter(user_id=user_id)
        .order_by(
            F('date_of_visit')
            .desc(nulls_last=True), 'city__title'
        )[:10])
