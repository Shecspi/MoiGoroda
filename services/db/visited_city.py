from django.db.models import F, QuerySet

from city.models import VisitedCity, City


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


def calculate_ratio(divisible: int, divisor: int) -> int:
    """
    Рассчитывает процентное соотношение divisible к divisor и возвращает его в округлённом до целого числа значении.
    """
    try:
        return int((divisible / divisor) * 100)
    except ZeroDivisionError:
        return 0


def get_last_10_visited_cities(user_id: int) -> QuerySet:
    """
    Возвращает последние 10 посещённых городов пользователя с ID, указанным в user_id.
    """
    return VisitedCity.objects.order_by(F('date_of_visit').desc(nulls_last=True), 'city__title')[:10]
