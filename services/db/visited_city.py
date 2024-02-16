import datetime

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
    return (VisitedCity.objects.filter(user=user_id)
            .annotate(month_year=TruncMonth('date_of_visit'))
            .values('month_year')
            .order_by('-month_year')
            .exclude(month_year=None)
            .annotate(qty=Count('id', distinct=True))
            .values('month_year', 'qty'))[:24]


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

    context['cities'] = {
        'number_of_visited_cities': 345,
        'number_of_not_visited_cities': get_number_of_cities() - 345,
        'last_10_visited_cities': [
            {'title': 'Москва', 'date_of_visit': '15.02.2024'},
            {'title': 'Санкт-Петербург', 'date_of_visit': '10.02.2024'},
            {'title': 'Удомля', 'date_of_visit': '31.01.2024'},
            {'title': 'Вышний Волочёк', 'date_of_visit': '30.01.2024'},
            {'title': 'Дрезна', 'date_of_visit': '22.01.2024'},
            {'title': 'Ахчой-Мартан', 'date_of_visit': '15.01.2024'},
            {'title': 'Грозный', 'date_of_visit': '14.01.2024'},
            {'title': 'Калининград', 'date_of_visit': '31.12.2023'},
            {'title': 'Владивосток', 'date_of_visit': '23.12.2023'},
            {'title': 'Кранознаменск', 'date_of_visit': '05.12.2023'},
        ],
        'number_of_visited_cities_current_year': 38,
        'number_of_visited_cities_previous_year': 55,
        'ratio_cities_this_year': calculate_ratio(38, 55),
        'ratio_cities_prev_year': 100 - calculate_ratio(38, 55),
        'number_of_visited_cities_in_several_years': (
            {'year': datetime.datetime.strptime('2024', '%Y'), 'qty': 38},
            {'year': datetime.datetime.strptime('2023', '%Y'), 'qty': 55},
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
        'number_of_visited_regions': 45,
        'number_of_not_visited_regions': number_of_regions - 45,
        'number_of_finished_regions': 10,
        'number_of_not_finished_regions': number_of_regions - 10,
        'ratio_visited_regions': calculate_ratio(45, number_of_regions),
        'ratio_not_visited_regions': calculate_ratio(number_of_regions - 45, number_of_regions),
        'ratio_finished_regions': calculate_ratio(10, number_of_regions),
        'ratio_not_finished_regions': calculate_ratio(number_of_regions - 10, number_of_regions),
        'number_of_half_finished_regions': 11
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
            'number_of_visited_cities': modification__city(345),
            'number_of_not_visited_cities': modification__city(790),
            'number_of_visited_cities_current_year': modification__city(38),
            'number_of_visited_cities_previous_year': modification__city(55)
        },
        'region': {
            'number_of_visited_regions': modification__region__prepositional_case(45),
            'number_of_not_visited_regions': modification__region__accusative_case(number_of_regions - 45),
            'number_of_finished_regions': modification__region__prepositional_case(10),
            'number_of_half_finished_regions': modification__region__prepositional_case(11),

        },
        'visited': {
            'number_of_visited_cities_previous_year': modification__visited(55)
        }
    }

    return context
