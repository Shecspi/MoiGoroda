"""
Реализует функцию, генерирующую поддельные данные для страницы статистики.
----------------------------------------------

Copyright 2024 Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

import datetime
from typing import Any

from services.calculate import calculate_ratio
from services.db.statistics.visited_city import get_number_of_cities
from services.db.statistics.visited_region import get_number_of_regions
from services.word_modifications.city import modification__city
from services.word_modifications.visited import modification__visited
from services.word_modifications.region import (
    modification__region__prepositional_case,
    modification__region__accusative_case,
)


def get_fake_statistics() -> dict[str, Any]:
    """
    Возвращает словарь, в котором находятся поддельные данные для использования на странице личной статистики.
    """
    context = {}

    tmp_number_of_visited_cities = 345
    tmp_number_of_total_visited_cities_current_year = 35
    tmp_number_of_total_visited_cities_previous_year = 59
    tmp_number_of_visited_regions = 46
    tmp_number_of_finished_regions = 13
    tmp_number_of_half_finished_regions = 18

    context['cities'] = {
        # Города - Общее количество
        'number_of_new_visited_cities': 542,
        'number_of_visited_cities': tmp_number_of_visited_cities,
        'list_of_all_countries_with_visited_cities': [
            {'name': 'Россия', 'visited_cities': 358, 'total_cities': 1253},
            {'name': 'Беларусь', 'visited_cities': 87, 'total_cities': 115},
            {'name': 'Казахстан', 'visited_cities': 54, 'total_cities': 90},
            {'name': 'Грузия', 'visited_cities': 42, 'total_cities': 55},
        ],
        # Города - В этом году
        'number_of_new_visited_cities_current_year': 28,
        'number_of_visited_cities_current_year': 34,
        'list_of_countries_with_new_visited_cities_current_year': [
            {
                'name': 'Россия',
                'visited_cities': 18,
            },
            {
                'name': 'Беларусь',
                'visited_cities': 10,
            },
        ],
        'list_of_countries_with_visited_cities_current_year': [
            {
                'name': 'Россия',
                'visited_cities': 22,
            },
            {
                'name': 'Беларусь',
                'visited_cities': 12,
            },
        ],
        # Города - В прошлом году
        'number_of_new_visited_cities_previous_year': 17,
        'number_of_visited_cities_previous_year': 19,
        'list_of_countries_with_new_visited_cities_previous_year': [
            {
                'name': 'Россия',
                'visited_cities': 10,
            },
            {
                'name': 'Беларусь',
                'visited_cities': 7,
            },
        ],
        'list_of_countries_with_visited_cities_previous_year': [
            {
                'name': 'Россия',
                'visited_cities': 12,
            },
            {
                'name': 'Беларусь',
                'visited_cities': 7,
            },
        ],
        ###
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
        'number_of_total_visited_cities_current_year': tmp_number_of_total_visited_cities_current_year,
        'number_of_total_visited_cities_previous_year': tmp_number_of_total_visited_cities_previous_year,
        'ratio_cities_this_year': calculate_ratio(
            tmp_number_of_total_visited_cities_current_year,
            tmp_number_of_total_visited_cities_previous_year,
        ),
        'ratio_cities_prev_year': 100
        - calculate_ratio(
            tmp_number_of_total_visited_cities_current_year,
            tmp_number_of_total_visited_cities_previous_year,
        ),
        'number_of_visited_cities_in_several_years': (
            {
                'year': datetime.datetime.strptime('2024', '%Y'),
                'qty': tmp_number_of_total_visited_cities_current_year,
            },
            {
                'year': datetime.datetime.strptime('2023', '%Y'),
                'qty': tmp_number_of_total_visited_cities_previous_year,
            },
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
        ),
    }

    number_of_regions = get_number_of_regions()
    context['regions'] = {
        # Регионы - общее количество
        'list_of_countries_with_visited_regions': [
            {
                'name': 'Россия',
                'number_of_regions': 89,
                'number_of_visited_regions': 21,
            },
            {
                'name': 'Беларусь',
                'number_of_regions': 7,
                'number_of_visited_regions': 7,
            },
            {
                'name': 'Казахстан',
                'number_of_regions': 20,
                'number_of_visited_regions': 5,
            },
            {
                'name': 'Грузия',
                'number_of_regions': 11,
                'number_of_visited_regions': 4,
            },
        ],
        # Регионы - В этом году
        'list_of_countries_with_visited_regions_current_year': [
            {
                'name': 'Россия',
                'number_of_regions': 89,
                'number_of_visited_regions': 10,
            },
        ],
        'list_of_countries_with_visited_regions_previous_year': [
            {
                'name': 'Россия',
                'number_of_regions': 89,
                'number_of_visited_regions': 5,
            },
        ],
        ###
        'most_visited_regions': (
            {
                'title': 'Тверская область',
                'num_visited': 21,
                'num_total': 23,
                'ratio_visited': int((21 / 23) * 100),
            },
            {
                'title': 'Чеченская республика',
                'num_visited': 7,
                'num_total': 8,
                'ratio_visited': int((7 / 8) * 100),
            },
            {
                'title': 'Москва',
                'num_visited': 4,
                'num_total': 5,
                'ratio_visited': int((4 / 5) * 100),
            },
            {
                'title': 'Московская область',
                'num_visited': 59,
                'num_total': 74,
                'ratio_visited': int((59 / 74) * 100),
            },
            {
                'title': 'Адыгея',
                'num_visited': 1,
                'num_total': 2,
                'ratio_visited': int((1 / 2) * 100),
            },
            {
                'title': 'Ярославская область',
                'num_visited': 4,
                'num_total': 11,
                'ratio_visited': int((4 / 11) * 100),
            },
            {
                'title': 'Севастополь',
                'num_visited': 1,
                'num_total': 3,
                'ratio_visited': int((1 / 3) * 100),
            },
            {
                'title': 'Волгоградская область',
                'num_visited': 4,
                'num_total': 15,
                'ratio_visited': int((4 / 15) * 100),
            },
            {
                'title': 'Краснодарский край',
                'num_visited': 6,
                'num_total': 26,
                'ratio_visited': int((6 / 26) * 100),
            },
            {
                'title': 'Владимирская область',
                'num_visited': 5,
                'num_total': 23,
                'ratio_visited': int((5 / 23) * 100),
            },
        ),
        'number_of_visited_regions': tmp_number_of_visited_regions,
        'number_of_not_visited_regions': number_of_regions - tmp_number_of_visited_regions,
        'number_of_finished_regions': tmp_number_of_finished_regions,
        'number_of_not_finished_regions': number_of_regions - tmp_number_of_finished_regions,
        'ratio_visited_regions': calculate_ratio(tmp_number_of_visited_regions, number_of_regions),
        'ratio_not_visited_regions': calculate_ratio(
            number_of_regions - tmp_number_of_visited_regions, number_of_regions
        ),
        'ratio_finished_regions': calculate_ratio(
            tmp_number_of_finished_regions, number_of_regions
        ),
        'ratio_not_finished_regions': calculate_ratio(
            number_of_regions - tmp_number_of_finished_regions, number_of_regions
        ),
        'number_of_half_finished_regions': tmp_number_of_half_finished_regions,
    }

    context['areas'] = {}
    context['areas']['list_of_areas'] = (
        {
            'title': 'Южный',
            'visited_regions': 7,
            'total_regions': 8,
            'ratio_visited': int((7 / 8) * 100),
        },
        {
            'title': 'Приволжский',
            'visited_regions': 8,
            'total_regions': 14,
            'ratio_visited': int((8 / 14) * 100),
        },
        {
            'title': 'Центральный',
            'visited_regions': 9,
            'total_regions': 18,
            'ratio_visited': int((9 / 18) * 100),
        },
        {
            'title': 'Северо-Западный',
            'visited_regions': 4,
            'total_regions': 11,
            'ratio_visited': int((4 / 11) * 100),
        },
        {
            'title': 'Северо-Кавказский',
            'visited_regions': 2,
            'total_regions': 7,
            'ratio_visited': int((2 / 7) * 100),
        },
        {
            'title': 'Уральский',
            'visited_regions': 1,
            'total_regions': 6,
            'ratio_visited': int((1 / 6) * 100),
        },
        {
            'title': 'Дальневосточный',
            'visited_regions': 0,
            'total_regions': 11,
            'ratio_visited': int((0 / 11) * 100),
        },
        {
            'title': 'Сибирский',
            'visited_regions': 0,
            'total_regions': 10,
            'ratio_visited': int((0 / 10) * 100),
        },
    )

    context['word_modifications'] = {
        'city': {
            'number_of_visited_cities': modification__city(tmp_number_of_visited_cities),
            'number_of_not_visited_cities': modification__city(
                get_number_of_cities() - tmp_number_of_visited_cities
            ),
            'number_of_visited_cities_current_year': modification__city(
                tmp_number_of_total_visited_cities_current_year
            ),
            'number_of_visited_cities_previous_year': modification__city(
                tmp_number_of_total_visited_cities_previous_year
            ),
        },
        'region': {
            'number_of_visited_regions': modification__region__accusative_case(
                tmp_number_of_visited_regions
            ),
            'number_of_not_visited_regions': modification__region__accusative_case(
                number_of_regions - tmp_number_of_visited_regions
            ),
            'number_of_finished_regions': modification__region__prepositional_case(
                tmp_number_of_finished_regions
            ),
            'number_of_half_finished_regions': modification__region__prepositional_case(
                tmp_number_of_half_finished_regions
            ),
        },
        'visited': {
            'number_of_visited_cities': modification__visited(tmp_number_of_visited_cities),
            'number_of_visited_regions': modification__visited(tmp_number_of_visited_regions),
            'number_of_visited_cities_previous_year': modification__visited(
                tmp_number_of_total_visited_cities_previous_year
            ),
        },
    }

    return context
