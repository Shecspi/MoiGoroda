from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import (
    OuterRef,
    Count,
    Avg,
    Exists,
    Q,
    Min,
    Max,
    Subquery,
    IntegerField,
    QuerySet,
    Func,
)
from django.db.models.functions import Round

from city.models import VisitedCity, City


class ExtractYearFromArray(Func):
    function = 'EXTRACT'
    template = '%(function)s(YEAR FROM unnest(%(expressions)s))'

    def __init__(self, expression, **extra):
        expressions = [expression]
        super().__init__(*expressions, **extra)


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
        * `number_of_visits` - количество посещений городп
        (для отображения названия региона лучше использовать просто `region`,
        а не `region.title` и `region.type`, так как `region` через __str__()
        отображает корректное обработанное название)
    """
    # Подзапрос для количества посещений города пользователем
    city_visits_subquery = (
        VisitedCity.objects.filter(user_id=user_id, city_id=OuterRef('city_id'))
        .values('city_id')  # Группировка по городу
        .annotate(count=Count('*'))  # Подсчет записей (число посещений)
        .values('count')  # Передаем только поле count
    )

    # Подзапрос для вычисления среднего рейтинга посещений города пользователем
    average_rating_subquery = (
        VisitedCity.objects.filter(user_id=user_id, city_id=OuterRef('city_id'))
        .values('city_id')  # Группировка по городу
        .annotate(avg_rating=Avg('rating'))  # Вычисление среднего рейтинга
        .values('avg_rating')  # Передаем только рейтинг
    )

    # Есть ли сувенир из города?
    has_souvenir = Exists(
        VisitedCity.objects.filter(city_id=OuterRef('city_id'), user_id=user_id, has_magnet=True)
    )

    # Подзапрос для сбора всех дат посещений города
    visit_dates_subquery = (
        VisitedCity.objects.filter(user_id=user_id, city=OuterRef('city__id'))
        .values('city')
        .annotate(
            visit_dates=ArrayAgg('date_of_visit', distinct=False, filter=~Q(date_of_visit=None))
        )
        .values('visit_dates')
    )

    # Подзапрос для даты первого посещения (first_visit_date)
    first_visit_date_subquery = (
        VisitedCity.objects.filter(user_id=user_id, city=OuterRef('city__id'))
        .values('city')
        .annotate(first_visit_date=Min('date_of_visit'))
        .values('first_visit_date')
    )

    # Подзапрос для даты последнего посещения (first_visit_date)
    last_visit_date_subquery = (
        VisitedCity.objects.filter(user_id=user_id, city=OuterRef('city__id'))
        .values('city')
        .annotate(last_visit_date=Max('date_of_visit'))
        .values('last_visit_date')
    )

    queryset = (
        VisitedCity.objects.filter(user_id=user_id, is_first_visit=True)
        .select_related('city', 'city__region', 'user')
        .annotate(
            number_of_visits=Subquery(city_visits_subquery, output_field=IntegerField()),
            average_rating=(
                Round((Subquery(average_rating_subquery) * 2), 0) / 2
            ),  # Округление до 0.5
            visit_dates=Subquery(visit_dates_subquery),
            first_visit_date=Subquery(first_visit_date_subquery),
            last_visit_date=Subquery(last_visit_date_subquery),
            has_souvenir=has_souvenir,
        )
    )

    return queryset


def get_number_of_cities() -> int:
    """
    Возвращает количество городов, сохранённых в базе данных.
    """
    return City.objects.count()


def get_number_of_visited_cities(user_id: int) -> int:
    """
    Возвращает количество городов, посещённых пользователем с user_id.
    """
    return get_all_visited_cities(user_id).count()


def get_number_of_not_visited_cities(user_id: int) -> int:
    """
    Возвращает количество непосещённых городов пользователем с ID, указанном в user_id.
    """
    return City.objects.count() - get_number_of_visited_cities(user_id)


def get_number_of_total_visited_cities_by_year(user_id: int, year: int) -> int:
    """
    Возвращает количество посещённых городов пользователем с ID, указанном в user_id, за один год, указанный в year.
    Учитываются все посещённые города, а не только уникальные.
    """
    result = 0
    for city in get_all_visited_cities(user_id):
        if city.visit_dates:
            for visit_date in city.visit_dates:
                if visit_date.year == year:
                    result += 1
    return result


def get_number_of_new_visited_cities_by_year(user_id: int, year: int) -> int:
    """
    Возвращает количество посещённых городов пользователем с ID, указанном в user_id, за один год, указанный в year.
    Учитываются только новые посещённые города.
    """
    result = 0
    for city in get_all_visited_cities(user_id):
        if city.visit_dates and min(city.visit_dates).year == year:
            result += 1
    return result
