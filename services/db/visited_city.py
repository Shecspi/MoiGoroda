import datetime
import calendar

from django.db.models import F, QuerySet, Count
from django.db.models.functions import TruncYear, TruncMonth

from city.models import VisitedCity, City
from services.db.statistics_of_visited_regions import get_number_of_regions
from services.word_modifications import modification__city
from services.word_modifications.modification__city import modification__city
from services.word_modifications.modification__visited import modification__visited
from services.word_modifications.modification_region import modification__region__accusative_case, \
    modification__region__prepositional_case


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

    # В график идут последние 24 месяца, для этого вычисляется месяц отсчёта и месяц завершения графика.
    # Для того чтобы первый и последний месяцы полностью попали в расчёт, нужно в первом месяце
    # указать началом 1 день, а в последнем - последний.
    now = datetime.datetime.now()
    start_date = datetime.date(now.year - 2, now.month + 1, 1)
    last_day_of_end_month = calendar.monthrange(now.year, now.month)[1]
    end_date = datetime.date(now.year, now.month, last_day_of_end_month)

    result = (
        VisitedCity.objects.filter(user=user_id)
        .filter(date_of_visit__range=(start_date, end_date))
        .annotate(month_year=TruncMonth('date_of_visit'))
        .values('month_year')
        .order_by('-month_year')
        .exclude(month_year=None)
        .annotate(qty=Count('id', distinct=True))
        .values('month_year', 'qty')
    )

    return result


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


def get_fake_statistics():
    context = {}

    tmp_number_of_visited_cities = 345
    tmp_number_of_visited_cities_current_year = 35
    tmp_number_of_visited_cities_previous_year = 59
    tmp_number_of_visited_regions = 46
    tmp_number_of_finished_regions = 13
    tmp_number_of_half_finished_regions = 18

    context['cities'] = {
        'number_of_visited_cities': tmp_number_of_visited_cities,
        'number_of_not_visited_cities': get_number_of_cities() - tmp_number_of_visited_cities,
        'last_10_visited_cities': (
            {'title': 'Донецк', 'date_of_visit': '16 февраля 2024 г.'},
            {'title': 'Ялта', 'date_of_visit': '14 февраля 2024 г.'},
            {'title': 'Белгород', 'date_of_visit': '30 декабря 2023 г.'},
            {'title': 'Бологое', 'date_of_visit': '23 августа 2023 г.'},
            {'title': 'Нижний Новгород', 'date_of_visit': '6 мая 2023 г.'},
            {'title': 'Москва', 'date_of_visit': '3 мая 2023 г.'},
            {'title': 'Химки', 'date_of_visit': '6 апреля 2023 г.'},
            {'title': 'Санкт-Петербург', 'date_of_visit': '2 апреля 2023 г.'},
            {'title': 'Энгельс', 'date_of_visit': '5 декабря 2022 г.'},
            {'title': 'Керчь', 'date_of_visit': '8 октября 2022 г.'},
            {'title': 'Голицыно', 'date_of_visit': '20 августа 2022 г.'},
        ),
        'number_of_visited_cities_current_year': tmp_number_of_visited_cities_current_year,
        'number_of_visited_cities_previous_year': tmp_number_of_visited_cities_previous_year,
        'ratio_cities_this_year': calculate_ratio(
            tmp_number_of_visited_cities_current_year,
            tmp_number_of_visited_cities_previous_year
        ),
        'ratio_cities_prev_year': 100 - calculate_ratio(
            tmp_number_of_visited_cities_current_year,
            tmp_number_of_visited_cities_previous_year
        ),
        'number_of_visited_cities_in_several_years': (
            {'year': datetime.datetime.strptime('2024', '%Y'), 'qty': tmp_number_of_visited_cities_current_year},
            {'year': datetime.datetime.strptime('2023', '%Y'), 'qty': tmp_number_of_visited_cities_previous_year},
            {'year': datetime.datetime.strptime('2022', '%Y'), 'qty': 47},
            {'year': datetime.datetime.strptime('2021', '%Y'), 'qty': 30},
            {'year': datetime.datetime.strptime('2020', '%Y'), 'qty': 22},
            {'year': datetime.datetime.strptime('2019', '%Y'), 'qty': 27},
            {'year': datetime.datetime.strptime('2018', '%Y'), 'qty': 12},
            {'year': datetime.datetime.strptime('2017', '%Y'), 'qty': 24},
            {'year': datetime.datetime.strptime('2016', '%Y'), 'qty': 7},
            {'year': datetime.datetime.strptime('2015', '%Y'), 'qty': 11},
            {'year': datetime.datetime.strptime('2014', '%Y'), 'qty': 3},
            {'year': datetime.datetime.strptime('2013', '%Y'), 'qty': 4},
            {'year': datetime.datetime.strptime('2012', '%Y'), 'qty': 3},
        ),
        'number_of_visited_cities_in_several_month': (
            {'month_year': datetime.datetime.strptime('122024', '%m%Y'), 'qty': 2},
            {'month_year': datetime.datetime.strptime('112024', '%m%Y'), 'qty': 5},
            {'month_year': datetime.datetime.strptime('102024', '%m%Y'), 'qty': 3},
            {'month_year': datetime.datetime.strptime('092024', '%m%Y'), 'qty': 2},
            {'month_year': datetime.datetime.strptime('082024', '%m%Y'), 'qty': 1},
            {'month_year': datetime.datetime.strptime('072024', '%m%Y'), 'qty': 5},
            {'month_year': datetime.datetime.strptime('062024', '%m%Y'), 'qty': 4},
            {'month_year': datetime.datetime.strptime('052024', '%m%Y'), 'qty': 2},
            {'month_year': datetime.datetime.strptime('042024', '%m%Y'), 'qty': 4},
            {'month_year': datetime.datetime.strptime('032024', '%m%Y'), 'qty': 4},
            {'month_year': datetime.datetime.strptime('022024', '%m%Y'), 'qty': 2},
            {'month_year': datetime.datetime.strptime('012024', '%m%Y'), 'qty': 3},
            {'month_year': datetime.datetime.strptime('122023', '%m%Y'), 'qty': 3},
            {'month_year': datetime.datetime.strptime('112023', '%m%Y'), 'qty': 3},
            {'month_year': datetime.datetime.strptime('102023', '%m%Y'), 'qty': 2},
            {'month_year': datetime.datetime.strptime('092023', '%m%Y'), 'qty': 3},
            {'month_year': datetime.datetime.strptime('082023', '%m%Y'), 'qty': 2},
            {'month_year': datetime.datetime.strptime('072023', '%m%Y'), 'qty': 4},
            {'month_year': datetime.datetime.strptime('062023', '%m%Y'), 'qty': 3},
            {'month_year': datetime.datetime.strptime('052023', '%m%Y'), 'qty': 2},
            {'month_year': datetime.datetime.strptime('042023', '%m%Y'), 'qty': 3},
            {'month_year': datetime.datetime.strptime('032023', '%m%Y'), 'qty': 1},
            {'month_year': datetime.datetime.strptime('022023', '%m%Y'), 'qty': 2},
            {'month_year': datetime.datetime.strptime('012023', '%m%Y'), 'qty': 2},
        )
    }

    number_of_regions = get_number_of_regions()
    context['regions'] = {
        'most_visited_regions': (
            {'title': 'Тверская область', 'visited_cities': 21,
             'total_cities': 23, 'ratio_visited': int((21/23) * 100)},
            {'title': 'Чеченская республика', 'visited_cities': 7,
             'total_cities': 8, 'ratio_visited': int((7/8) * 100)},
            {'title': 'Москва', 'visited_cities': 4,
             'total_cities': 5, 'ratio_visited': int((4/5) * 100)},
            {'title': 'Московская область', 'visited_cities': 59,
             'total_cities': 74, 'ratio_visited': int((59/74) * 100)},
            {'title': 'Адыгея', 'visited_cities': 1,
             'total_cities': 2, 'ratio_visited': int((1/2) * 100)},
            {'title': 'Ярославская область', 'visited_cities': 4,
             'total_cities': 11, 'ratio_visited': int((4/11) * 100)},
            {'title': 'Севастополь', 'visited_cities': 1,
             'total_cities': 3, 'ratio_visited': int((1/3) * 100)},
            {'title': 'Волгоградская область', 'visited_cities': 4,
             'total_cities': 15, 'ratio_visited': int((4/15) * 100)},
            {'title': 'Краснодарский край', 'visited_cities': 6,
             'total_cities': 26, 'ratio_visited': int((6/26) * 100)},
            {'title': 'Владимирская область', 'visited_cities': 5,
             'total_cities': 23, 'ratio_visited': int((5/23) * 100)},
        ),
        'number_of_visited_regions': tmp_number_of_visited_regions,
        'number_of_not_visited_regions': number_of_regions - tmp_number_of_visited_regions,
        'number_of_finished_regions': tmp_number_of_finished_regions,
        'number_of_not_finished_regions': number_of_regions - tmp_number_of_finished_regions,
        'ratio_visited_regions': calculate_ratio(tmp_number_of_visited_regions, number_of_regions),
        'ratio_not_visited_regions': calculate_ratio(number_of_regions - tmp_number_of_visited_regions, number_of_regions),
        'ratio_finished_regions': calculate_ratio(tmp_number_of_finished_regions, number_of_regions),
        'ratio_not_finished_regions': calculate_ratio(number_of_regions - tmp_number_of_finished_regions, number_of_regions),
        'number_of_half_finished_regions': tmp_number_of_half_finished_regions
    }

    context['areas'] = (
        {'title': 'Южный', 'visited_regions': 7, 'total_regions': 8, 'ratio_visited': int((7 / 8) * 100)},
        {'title': 'Приволжский', 'visited_regions': 8, 'total_regions': 14, 'ratio_visited': int((8 / 14) * 100)},
        {'title': 'Центральный', 'visited_regions': 9, 'total_regions': 18, 'ratio_visited': int((9 / 18) * 100)},
        {'title': 'Северо-Западный', 'visited_regions': 4, 'total_regions': 11, 'ratio_visited': int((4 / 11) * 100)},
        {'title': 'Северо-Кавказский', 'visited_regions': 2, 'total_regions': 7, 'ratio_visited': int((2 / 7) * 100)},
        {'title': 'Уральский', 'visited_regions': 1, 'total_regions': 6, 'ratio_visited': int((1 / 6) * 100)},
        {'title': 'Дальневосточный', 'visited_regions': 0, 'total_regions': 11, 'ratio_visited': int((0 / 11) * 100)},
        {'title': 'Сибирский', 'visited_regions': 0, 'total_regions': 10, 'ratio_visited': int((0 / 10) * 100)},
    )

    context['word_modifications'] = {
        'city': {
            'number_of_visited_cities': modification__city(tmp_number_of_visited_cities),
            'number_of_not_visited_cities': modification__city(get_number_of_cities() - tmp_number_of_visited_cities),
            'number_of_visited_cities_current_year': modification__city(tmp_number_of_visited_cities_current_year),
            'number_of_visited_cities_previous_year': modification__city(tmp_number_of_visited_cities_previous_year)
        },
        'region': {
            'number_of_visited_regions': modification__region__prepositional_case(tmp_number_of_visited_regions),
            'number_of_not_visited_regions': modification__region__accusative_case(number_of_regions - tmp_number_of_visited_regions),
            'number_of_finished_regions': modification__region__prepositional_case(tmp_number_of_finished_regions),
            'number_of_half_finished_regions': modification__region__prepositional_case(tmp_number_of_half_finished_regions),

        },
        'visited': {
            'number_of_visited_cities_previous_year': modification__visited(tmp_number_of_visited_cities_previous_year)
        }
    }

    return context
