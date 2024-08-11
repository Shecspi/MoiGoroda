"""
Реализует функции, взаимодействующие с моделью VisitedCity.
Любая работа с этой моделью должна происходить только через описанные в этом файле функции.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime
from typing import Literal, Sequence

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet, F, Case, When, Value

from city.models import VisitedCity, City


def order_by_date_of_visit_desc(cities: QuerySet[VisitedCity]):
    """
    Производит сортировку QuerySet по столбцу 'date_of_visit', если такой имеется, в уменьшающемся порядке.
    Если QuerySet пуст или столбца 'date_of_visit' не существует - возвращается оригинальный QuerySet без изменений.
    """
    if cities and hasattr(cities[0], 'date_of_visit'):
        return cities.order_by(F('date_of_visit').desc(nulls_last=True))
    else:
        return cities


def order_by_date_of_visit_asc(cities: QuerySet[VisitedCity]):
    """
    Производит сортировку QuerySet по столбцу 'date_of_visit', если такой имеется, в увеличивающемся порядке.
    Если QuerySet пуст или столбца 'date_of_visit' не существует - возвращается оригинальный QuerySet без изменений.
    """
    if cities and hasattr(cities[0], 'date_of_visit'):
        return cities.order_by(F('date_of_visit').asc(nulls_last=True))
    else:
        return cities


def get_visited_city(user_id: int, city_id: int) -> VisitedCity | Literal[False]:
    """
    Возвращает экземпляр класса VisitedCity с информацией о посещённом городе, если запись,
    соответствующая указанным в user_id и city_id параметрах, существует. Иначе возвращает False.
    """
    try:
        return VisitedCity.objects.get(user_id=user_id, id=city_id)
    except ObjectDoesNotExist:
        return False


def get_all_visited_cities(user_id: int) -> QuerySet[VisitedCity]:
    """
    Получает из базы данных все посещённые города пользователя с ID, указанным в user_id.
    Возвращает Queryset, состоящий из полей:
        * `id` - ID посещённого города
        * `date_of_visit` - дата посещения города
        * `rating` - рейтинг посещённого города
        * `has_magnet` - наличие сувенира из города
        * `city.id` - ID города
        * `city.title` - Название города
        * `city.population` - население города
        * `city.date_of_foundation` - дата основания города
        * `city.coordinate_width` - широта
        * `city.coordinate_longitude` - долгота
        * `region.id` - ID региона, в котором расположен город
        * `region.title` - название региона, в котором расположен город
        * `region.type` - тип региона, в котором расположен город
        (для отображение названия региона лучше использовать просто `region`,
        а не `region.title` и `region.type`, так как `region` через __str__()
        отображает корректное обработанное название)
    """
    return (
        VisitedCity.objects.filter(user_id=user_id)
        .select_related('city', 'region')
        .only(
            'id',
            'date_of_visit',
            'rating',
            'has_magnet',
            'city__id',
            'city__title',
            'city__population',
            'city__date_of_foundation',
            'city__coordinate_width',
            'city__coordinate_longitude',
            'region__id',
            'region__title',
            'region__type',
        )
    )


def get_visited_cities_many_users(
    user_ids: Sequence[int], select_related_fields: Sequence[str], fields: Sequence[str]
) -> QuerySet[VisitedCity]:
    return (
        VisitedCity.objects.filter(user_id__in=user_ids)
        .select_related(*select_related_fields)
        .only(*fields)
    )


def get_not_visited_cities(user_id: int, regions: dict[int, str]) -> QuerySet[City]:
    """
    Возвращает QuerySet объектов City, которые пользователь с ID user_id не отметил, как посещённые.
    Для этого берётся список всех городов, которые есть в БД, и из него убираются уже посещённые пользователем города.
    При этом для каждого объекта City добавляется дополнительное поле 'region_title',
    в котором сохраняется человекочитаемое название.
    """
    visited_cities = [city.city.id for city in get_all_visited_cities(user_id)]

    # Для получения человекочитаемого формата используется сложная конструкция с Case, When и дополнительным словарём
    # регионов, так как прямое обращение к полю 'region' возвращает int, а не объект 'Region', из-за чего
    # становится невозмоным получить название региона. Точнее его получить можно, но только в том виде, в котором
    # оно хранится в БД, а не в человекочитаемом.
    # ToDo: Удалить эту доп. логику, когда будет выполнена задача #3.
    return City.objects.exclude(id__in=visited_cities).annotate(
        region_title=Case(
            *[
                When(region__pk=region_id, then=Value(region_title))
                for region_id, region_title in regions.items()
            ]
        )
    )


def get_number_of_visited_cities(user_id: int) -> int:
    """
    Возвращает количество городов, посещённых пользователем с user_id.
    """
    return get_all_visited_cities(user_id).count()


def get_number_of_visited_cities_current_year(user_id: int) -> int:
    """
    Возвращает количество городов, посещённых пользователем с user_id в текущем году.
    """
    return get_all_visited_cities(user_id).filter(date_of_visit__year=datetime.now().year).count()


def get_number_of_visited_cities_previous_year(user_id: int) -> int:
    """
    Возвращает количество городов, посещённых пользователем с user_id в прошлом году.
    """
    return (
        get_all_visited_cities(user_id).filter(date_of_visit__year=datetime.now().year - 1).count()
    )
