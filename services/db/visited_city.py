from django.db.models import F, QuerySet, Count
from django.db.models.functions import TruncYear, TruncMonth

from city.models import VisitedCity, City


def calculate_ratio(divisible: int, divisor: int) -> int:
    """
    Рассчитывает процентное соотношение divisible к divisor и возвращает его в округлённом до целого числа значении.
    В случае, если в качестве divisor передаётся 0, то возвращается 0.
    """
    try:
        return int((divisible / divisor) * 100)
    except ZeroDivisionError:
        return 0


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
    return (VisitedCity.objects.filter(user=user_id)
            .annotate(month_year=TruncMonth('date_of_visit'))
            .values('month_year')
            .order_by('-month_year')
            .exclude(month_year=None)
            .annotate(qty=Count('id', distinct=True))
            .values('month_year', 'qty'))[:24]


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
