import calendar
import datetime

from django.contrib.auth.base_user import AbstractBaseUser
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
    F,
    Window,
)
from django.db.models.functions import Round, TruncYear, TruncMonth, Rank

from city.models import VisitedCity, City


class ExtractYearFromArray(Func):
    function = 'EXTRACT'
    template = '%(function)s(YEAR FROM unnest(%(expressions)s))'

    def __init__(self, expression, **extra):
        expressions = [expression]
        super().__init__(*expressions, **extra)


def get_all_visited_cities(user_id: int, country_id: int | None = None) -> QuerySet[VisitedCity]:
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

    # Подзапрос для получения количество пользователей, посетивших город
    number_of_users_who_visit_city = (
        VisitedCity.objects.filter(city=OuterRef('city'), is_first_visit=True)
        .values('city_id')
        .annotate(count=Count('*'))
        .values('count')[:1]
    )

    # Подзапрос для получения общего количества посещений города
    number_of_visits_all_users = (
        VisitedCity.objects.filter(city=OuterRef('city__id'))
        .values('city_id')
        .annotate(count=Count('*'))
        .values('count')[:1]
    )

    if country_id:
        queryset = VisitedCity.objects.filter(city__country_id=country_id)
    else:
        queryset = VisitedCity.objects.all()

    queryset = (
        queryset.filter(user_id=user_id, is_first_visit=True)
        .select_related(
            'city',
            'city__region',
            'user',
        )
        .annotate(
            number_of_visits=Subquery(city_visits_subquery, output_field=IntegerField()),
            average_rating=(
                Round((Subquery(average_rating_subquery) * 2), 0) / 2
            ),  # Округление до 0.5
            visit_dates=Subquery(visit_dates_subquery),
            first_visit_date=Subquery(first_visit_date_subquery),
            last_visit_date=Subquery(last_visit_date_subquery),
            has_souvenir=has_souvenir,
            number_of_users_who_visit_city=Subquery(
                number_of_users_who_visit_city, output_field=IntegerField()
            ),
            number_of_visits_all_users=Subquery(number_of_visits_all_users),
        )
    )

    return queryset


def get_all_new_visited_cities(user_id: int) -> QuerySet[VisitedCity]:
    return VisitedCity.objects.filter(is_first_visit=True, user_id=user_id)


def get_number_of_cities(country_id: int | None = None) -> int:
    """
    Возвращает количество городов, сохранённых в базе данных.
    """
    queryset = City.objects.all()
    if country_id:
        queryset = queryset.filter(country_id=country_id)
    return queryset.count()


def get_number_of_cities_in_region_by_city(city_id: int) -> int:
    try:
        city = City.objects.get(id=city_id)
    except (City.DoesNotExist, City.MultipleObjectsReturned):
        return 0

    return City.objects.filter(region=city.region).count()


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
    for city in get_all_new_visited_cities(user_id):
        if city.date_of_visit and city.date_of_visit.year == year:
            result += 1
    return result


def get_last_10_new_visited_cities(user_id: int) -> QuerySet:
    """
    Возвращает последние 10 посещённых городов пользователя с ID, указанным в user_id.
    """
    return (
        get_all_visited_cities(user_id)
        .exclude(first_visit_date=None)
        .order_by('-first_visit_date')[:10]
    )


def get_number_of_total_visited_cities_in_several_years(user_id: int):
    """
    Возвращает общее количество посещённых городов за каждый год.
    """
    return (
        VisitedCity.objects.filter(user=user_id)
        .annotate(year=TruncYear('date_of_visit'))
        .values('year')
        .exclude(year=None)
        .annotate(qty=Count('id', distinct=True))
        .values('year', 'qty')
    )


def get_number_of_new_visited_cities_in_several_years(user_id: int):
    """
    Возвращает количество новых посещённых городов за каждый год.
    """
    return (
        VisitedCity.objects.filter(user=user_id)
        .filter(is_first_visit=True)
        .annotate(year=TruncYear('date_of_visit'))
        .values('year')
        .exclude(year=None)
        .annotate(qty=Count('id', distinct=True))
        .values('year', 'qty')
    )


def _get_visited_cities(user_id: int) -> QuerySet[VisitedCity]:
    now = datetime.datetime.now()
    if now.month == 12:
        start_date = datetime.date(now.year - 1, 1, 1)
    else:
        start_date = datetime.date(now.year - 2, now.month + 1, 1)
    last_day_of_end_month = calendar.monthrange(now.year, now.month)[1]
    end_date = datetime.date(now.year, now.month, last_day_of_end_month)

    return VisitedCity.objects.filter(user=user_id).filter(
        date_of_visit__range=(start_date, end_date)
    )


def get_number_of_total_visited_cities_in_several_month(user_id: int):
    """
    Возвращает статистику по количеству посещённых городов за каждый месяц (последние 24 месяца).
    """

    # В график идут последние 24 месяца, для этого вычисляется месяц отсчёта и месяц завершения графика.
    # Для того чтобы первый и последний месяцы полностью попали в расчёт, нужно в первом месяце
    # указать началом 1 день, а в последнем - последний.

    return (
        _get_visited_cities(user_id)
        .annotate(month_year=TruncMonth('date_of_visit'))
        .values('month_year')
        .order_by('-month_year')
        .exclude(month_year=None)
        .annotate(qty=Count('id', distinct=True))
        .values('month_year', 'qty')
    )


def get_number_of_new_visited_cities_in_several_month(user_id: int):
    return (
        _get_visited_cities(user_id)
        .filter(is_first_visit=True)
        .annotate(month_year=TruncMonth('date_of_visit'))
        .values('month_year')
        .order_by('-month_year')
        .exclude(month_year=None)
        .annotate(qty=Count('id', distinct=True))
        .values('month_year', 'qty')
    )


def get_number_of_visits_by_city(city_id: int, user_id: int) -> int:
    return VisitedCity.objects.filter(city_id=city_id, user=user_id).count()


def get_first_visit_date_by_city(city_id: int, user_id: int) -> datetime.date:
    first_visit_date_subquery = (
        VisitedCity.objects.filter(user_id=user_id, city=OuterRef('city__id'))
        .values('city')
        .annotate(first_visit_date=Min('date_of_visit'))
        .values('first_visit_date')
    )

    return (
        VisitedCity.objects.filter(city_id=city_id, user=user_id)
        .annotate(first_visit_date=Subquery(first_visit_date_subquery))
        .first()
        .first_visit_date
    )


def get_last_visit_date_by_city(city_id: int, user_id: int) -> datetime.date:
    first_visit_date_subquery = (
        VisitedCity.objects.filter(user_id=user_id, city=OuterRef('city__id'))
        .values('city')
        .annotate(last_visit_date=Max('date_of_visit'))
        .values('last_visit_date')
    )

    return (
        VisitedCity.objects.filter(city_id=city_id, user=user_id)
        .annotate(last_visit_date=Subquery(first_visit_date_subquery))
        .first()
        .last_visit_date
    )


def set_is_visit_first_for_all_visited_cities(city_id: int, user: AbstractBaseUser):
    """
    Обновляет "is_first_visit" на True для посещения с самой ранней датой или без даты вообще.
    Для всех остальных посещений "is_first_visit" устанавливаем в False.
    """
    cities = VisitedCity.objects.filter(city_id=city_id, user=user).order_by(
        F('date_of_visit').asc(nulls_first=True)
    )

    if not cities:
        return

    first_id = cities[0].id

    # Массовое обновление всех is_first_visit = False
    VisitedCity.objects.filter(city_id=city_id, user=user).exclude(id=first_id).update(
        is_first_visit=False
    )

    # Обновляем только первую запись
    VisitedCity.objects.filter(id=first_id).update(is_first_visit=True)


def get_number_of_users_who_visit_city(city_id: int) -> int:
    return VisitedCity.objects.filter(city=city_id, is_first_visit=True).count()


def get_total_number_of_visits(country_id: int | None = False) -> int:
    """
    Возвращает общее количество посещённых городов всеми пользователями
    """
    queryset = VisitedCity.objects.select_related('city')
    if country_id:
        queryset = queryset.filter(city__country_id=country_id)
    return queryset.count()


def get_rank_by_visits_of_city(city_id: int, country_id: int | None = False) -> int:
    queryset = City.objects.all()
    if country_id:
        queryset = queryset.filter(country_id=country_id)

    ranked_cities = list(
        queryset.annotate(
            visits=Count('visitedcity'), rank=Window(expression=Rank(), order_by=F('visits').desc())
        )
        .values('id', 'title', 'visits', 'rank')
        .order_by('rank')
    )

    for city in ranked_cities:
        if city['id'] == city_id:
            return city['rank']

    return 0


def get_rank_by_users_of_city(city_id: int, country_id: int | None = False) -> int:
    queryset = City.objects.all()
    if country_id:
        queryset = queryset.filter(country_id=country_id)

    ranked_cities = list(
        queryset.annotate(
            visits=Count('visitedcity__user', distinct=True),
            rank=Window(expression=Rank(), order_by=F('visits').desc()),
        )
        .values('id', 'title', 'visits', 'rank')
        .order_by('rank')
    )

    for city in ranked_cities:
        if city['id'] == city_id:
            return city['rank']

    return 0


def get_rank_by_visits_of_city_in_region(city_id: int, is_country_filter: bool = False) -> int:
    """
    Возвращает местоположение города в рейтинге городов региона на основе количества посещений.
    По-умолчанию сравнивает со всеми городами, но можно ограничить выборку одной страной.
    Если в стране есть разбивка на регионы, то показывает рейтинг в этом регионе.
    Если такой разбивки нет, то в рейтинг пойдут все города страны.
    """
    try:
        city = City.objects.get(id=city_id)
    except (City.DoesNotExist, City.MultipleObjectsReturned):
        return 0

    queryset = City.objects.all()
    if is_country_filter:
        queryset = queryset.filter(country_id=city.country_id)
    if city.region:
        queryset = queryset.filter(region=city.region)
    ranked_cities = list(
        queryset.annotate(
            visits=Count('visitedcity'), rank=Window(expression=Rank(), order_by=F('visits').desc())
        )
        .values('id', 'title', 'visits', 'rank')
        .order_by('rank')
    )

    for city in ranked_cities:
        if city['id'] == city_id:
            return city['rank']

    return 0


def get_rank_by_users_of_city_in_region(city_id: int, is_country_filter: bool = False) -> int:
    """
    Возвращает местоположение города в рейтинге городов региона на основе количества пользователей, посетивших город.
    По-умолчанию сравнивает со всеми городами, но можно ограничить выборку одной страной.
    Если в стране есть разбивка на регионы, то показывает рейтинг в этом регионе.
    Если такой разбивки нет, то в рейтинг пойдут все города страны.
    """
    try:
        city = City.objects.get(id=city_id)
    except (City.DoesNotExist, City.MultipleObjectsReturned):
        return 0

    queryset = City.objects.all()
    if is_country_filter:
        queryset = queryset.filter(country_id=city.country_id)
    if city.region:
        queryset = queryset.filter(region=city.region)
    ranked_cities = list(
        queryset.annotate(
            visits=Count('visitedcity__user', distinct=True),
            rank=Window(expression=Rank(), order_by=F('visits').desc()),
        )
        .values('id', 'title', 'visits', 'rank')
        .order_by('rank')
    )

    for city in ranked_cities:
        if city['id'] == city_id:
            return city['rank']

    return 0


def _get_cities_near_index(items: list, city_id: int, window_size: int = 10) -> list:
    # Ищем индекс нужного города
    index = next((i for i, city in enumerate(items) if city['id'] == city_id), None)
    if index is None:
        return []

    # Выбираем 10 соседних городов
    start = max(index - 4, 0)
    end = start + 10
    if end > len(items):
        end = len(items)
        start = max(0, end - 10)

    return items[start:end]


def get_neighboring_cities_by_visits_rank(city_id: int, is_country_filter: bool = False):
    """
    Возвращает список 10 городов, которые располагаются близко к искомому городу.
    Выборка происходит по общему количеству посещений города всеми пользователями.
    """
    try:
        city = City.objects.get(id=city_id)
    except (City.DoesNotExist, City.MultipleObjectsReturned):
        return []

    queryset = City.objects.all()
    if is_country_filter:
        queryset = queryset.filter(country_id=city.country_id)
    ranked_cities = list(
        queryset.annotate(
            visits=Count('visitedcity__user', distinct=True),
            rank=Window(expression=Rank(), order_by=F('visits').desc()),
        )
        .values('id', 'title', 'visits', 'rank')
        .order_by('rank')
    )
    return _get_cities_near_index(ranked_cities, city_id)


def get_neighboring_cities_in_region_by_visits_rank(city_id: int, is_country_filter: bool = False):
    """
    Возвращает список 10 городов конкретного региона, которые располагаются близко к искомому городу.
    Выборка происходит по общему количеству посещений города всеми пользователями.
    """
    try:
        city = City.objects.get(id=city_id)
    except (City.DoesNotExist, City.MultipleObjectsReturned):
        return []

    queryset = City.objects.all()
    if is_country_filter:
        queryset = queryset.filter(country_id=city.country_id)
    ranked_cities = list(
        queryset.filter(region=city.region)
        .annotate(
            visits=Count('visitedcity__user', distinct=True),
            rank=Window(expression=Rank(), order_by=F('visits').desc()),
        )
        .values('id', 'title', 'visits', 'rank')
        .order_by('rank')
    )
    return _get_cities_near_index(ranked_cities, city_id)


def get_neighboring_cities_by_users_rank(city_id: int, is_country_filter: bool = False):
    """
    Возвращает список 10 городов, которые располагаются близко к искомому городу.
    Выборка происходит по общему количеству посещений города всеми пользователями.
    """
    try:
        city = City.objects.get(id=city_id)
    except (City.DoesNotExist, City.MultipleObjectsReturned):
        return []

    queryset = City.objects.all()
    if is_country_filter:
        queryset = queryset.filter(country_id=city.country_id)
    ranked_cities = list(
        queryset.annotate(
            visits=Count('visitedcity'),
            rank=Window(expression=Rank(), order_by=F('visits').desc()),
        )
        .values('id', 'title', 'visits', 'rank')
        .order_by('rank')
    )
    return _get_cities_near_index(ranked_cities, city_id)


def get_neighboring_cities_in_region_by_users_rank(city_id: int, is_country_filter: bool = False):
    """
    Возвращает список 10 городов конкретного региона, которые располагаются близко к искомому городу.
    Выборка происходит по общему количеству посещений города всеми пользователями.
    """
    try:
        city = City.objects.get(id=city_id)
    except (City.DoesNotExist, City.MultipleObjectsReturned):
        return []

    queryset = City.objects.all()
    if is_country_filter:
        queryset = queryset.filter(country_id=city.country_id)
    ranked_cities = list(
        queryset.filter(region=city.region)
        .annotate(
            visits=Count('visitedcity'),
            rank=Window(expression=Rank(), order_by=F('visits').desc()),
        )
        .values('id', 'title', 'visits', 'rank')
        .order_by('rank')
    )
    return _get_cities_near_index(ranked_cities, city_id)
