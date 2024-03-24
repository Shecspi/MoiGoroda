"""
Реализует функции, взаимодействующие с моделью City.
Любая работа с этой моделью должна происходить только через описанные в этом файле функции.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.db.models import QuerySet

from city.models import City
from collection.models import Collection


def get_number_of_cities() -> int:
    """
    Возвращает количество городов, сохранённых в базе данных.
    """
    return City.objects.count()


def get_list_of_collections(city_id: int) -> QuerySet[Collection]:
    """
    Возвращает QuerySet с коллекциями, в которых присутствует город с ID, равным city_id.
    """
    return City.objects.get(id=city_id).collections_list.all()
