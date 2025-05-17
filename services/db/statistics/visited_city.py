"""
Реализует функцию, генерирующую поддельные данные для страницы статистики.
----------------------------------------------

Copyright 2024 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

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
