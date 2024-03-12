from city.models import City


def get_number_of_cities() -> int:
    """
    Возвращает количество городов, сохранённых в базе данных.
    """
    return City.objects.count()
