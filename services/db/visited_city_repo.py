"""
Реализует функции, взаимодействующие с моделью VisitedCity.
Любая работа с этой моделью должна происходить только через описанные в этом файле функции.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Literal

from django.core.exceptions import ObjectDoesNotExist

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


def get_number_of_visited_cities(user_id: int) -> int:
    """
    Возвращает количество городов, посещённых пользователем с user_id.
    """
    return get_all_visited_cities(user_id).count()
