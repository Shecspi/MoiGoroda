from datetime import datetime
from typing import Literal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from city.models import VisitedCity


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
        * `has_magnet` - наличие магните
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
        VisitedCity.objects
        .filter(user_id=user_id)
        .select_related('city', 'region')
        .only(
            'id', 'date_of_visit', 'rating', 'has_magnet',
            'city__id', 'city__title', 'city__population', 'city__date_of_foundation',
            'city__coordinate_width', 'city__coordinate_longitude',
            'region__id', 'region__title', 'region__type'
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
    return get_all_visited_cities(user_id).filter(date_of_visit__year=datetime.now().year - 1).count()
