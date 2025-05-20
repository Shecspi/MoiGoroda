import datetime

from services.word_modifications.city import *
from services.calculate import calculate_ratio
from services.word_modifications.region import *
from services.word_modifications.visited import *
from city.services.db import (
    get_number_of_visited_cities,
    get_number_of_not_visited_cities,
    get_number_of_total_visited_cities_by_year,
    get_number_of_new_visited_cities_by_year,
    get_number_of_total_visited_cities_in_several_years,
    get_number_of_total_visited_cities_in_several_month,
    get_last_10_new_visited_cities,
    get_number_of_new_visited_cities_in_several_month,
    get_number_of_new_visited_cities_in_several_years,
)
from region.services.db import (
    get_number_of_visited_regions,
    get_number_of_finished_regions,
    get_all_region_with_visited_cities,
    get_number_of_regions,
    get_visited_areas,
    get_number_all_areas,
    get_number_visited_areas,
)


def get_info_for_statistic_cards_and_charts(user_id: int) -> dict:
    """
    Получает из БД большое количество информации по посещённым городам,
    регионам и округам и возвращает это в виде словаря.
    """
    context = {}
    current_year = datetime.datetime.now().year

    #################################
    # --- Статистика по городам --- #
    #################################
    number_of_visited_cities = get_number_of_visited_cities(user_id)
    number_of_not_visited_cities = get_number_of_not_visited_cities(user_id)

    number_of_total_visited_cities_current_year = get_number_of_total_visited_cities_by_year(
        user_id, current_year
    )
    number_of_new_visited_cities_current_year = get_number_of_new_visited_cities_by_year(
        user_id, current_year
    )
    number_of_total_visited_cities_previous_year = get_number_of_total_visited_cities_by_year(
        user_id, current_year - 1
    )
    number_of_new_visited_cities_previous_year = get_number_of_new_visited_cities_by_year(
        user_id, current_year - 1
    )
    ratio_cities_this_year = calculate_ratio(
        number_of_total_visited_cities_current_year, number_of_total_visited_cities_previous_year
    )
    ratio_cities_prev_year = 100 - ratio_cities_this_year

    number_of_total_visited_cities_in_several_years = (
        get_number_of_total_visited_cities_in_several_years(user_id)
    )
    number_of_new_visited_cities_in_several_years = (
        get_number_of_new_visited_cities_in_several_years(user_id)
    )
    number_of_total_visited_cities_in_several_month = (
        get_number_of_total_visited_cities_in_several_month(user_id)
    )
    number_of_new_visited_cities_in_several_month = (
        get_number_of_new_visited_cities_in_several_month(user_id)
    )

    context['cities'] = {
        'number_of_visited_cities': number_of_visited_cities,
        'number_of_not_visited_cities': number_of_not_visited_cities,
        'last_10_visited_cities': get_last_10_new_visited_cities(user_id),
        'number_of_total_visited_cities_current_year': number_of_total_visited_cities_current_year,
        'number_of_new_visited_cities_current_year': number_of_new_visited_cities_current_year,
        'number_of_total_visited_cities_previous_year': number_of_total_visited_cities_previous_year,
        'number_of_new_visited_cities_previous_year': number_of_new_visited_cities_previous_year,
        'ratio_cities_this_year': ratio_cities_this_year,
        'ratio_cities_prev_year': ratio_cities_prev_year,
        'number_of_total_visited_cities_in_several_years': number_of_total_visited_cities_in_several_years,
        'number_of_new_visited_cities_in_several_years': number_of_new_visited_cities_in_several_years,
        'number_of_total_visited_cities_in_several_month': number_of_total_visited_cities_in_several_month,
        'number_of_new_visited_cities_in_several_month': number_of_new_visited_cities_in_several_month,
    }

    ##################################
    # --- Статистика по регионам --- #
    ##################################
    regions = get_all_region_with_visited_cities(user_id)
    number_of_regions = get_number_of_regions()
    num_visited_regions = get_number_of_visited_regions(user_id)
    num_not_visited_regions = number_of_regions - num_visited_regions
    num_finished_regions = get_number_of_finished_regions(user_id)
    number_of_not_finished_regions = number_of_regions - num_finished_regions

    ratio_visited = calculate_ratio(
        num_visited_regions, num_visited_regions + num_not_visited_regions
    )
    ratio_not_visited = 100 - ratio_visited
    ratio_finished = calculate_ratio(
        num_finished_regions, num_finished_regions + num_not_visited_regions
    )
    ratio_not_finished = 100 - ratio_finished

    context['regions'] = {
        'most_visited_regions': regions[:10],
        'number_of_visited_regions': num_visited_regions,
        'number_of_not_visited_regions': num_not_visited_regions,
        'number_of_finished_regions': num_finished_regions,
        'number_of_not_finished_regions': number_of_not_finished_regions,
        'ratio_visited_regions': ratio_visited,
        'ratio_not_visited_regions': ratio_not_visited,
        'ratio_finished_regions': ratio_finished,
        'ratio_not_finished_regions': ratio_not_finished,
    }

    #############################################
    # --- Статистика по федеральным округам --- #
    #############################################
    areas = get_visited_areas(user_id)
    number_all_areas = get_number_all_areas()
    number_visited_areas = get_number_visited_areas(user_id)

    context['areas'] = {
        'list_of_areas': areas,
        'number_all_areas': number_all_areas,
        'number_visited_areas': number_visited_areas,
        'number_not_visited_areas': number_all_areas - number_visited_areas,
    }

    ####################
    # Изменённые слова #
    ####################
    context['word_modifications'] = {
        'city': {
            'number_of_visited_cities': modification__city(number_of_visited_cities),
            'number_of_not_visited_cities': modification__city(number_of_not_visited_cities),
            'number_of_total_visited_cities_current_year': modification__city(
                number_of_total_visited_cities_current_year
            ),
            'number_of_new_visited_cities_current_year': modification__city(
                number_of_new_visited_cities_current_year
            ),
            'number_of_total_visited_cities_previous_year': modification__city(
                number_of_total_visited_cities_previous_year
            ),
            'number_of_new_visited_cities_previous_year': modification__city(
                number_of_new_visited_cities_previous_year
            ),
        },
        'region': {
            'number_of_visited_regions': modification__region__accusative_case(num_visited_regions),
            'number_of_not_visited_regions': modification__region__accusative_case(
                number_of_regions - num_visited_regions
            ),
            'number_of_finished_regions': modification__region__prepositional_case(
                num_finished_regions
            ),
        },
        'visited': {
            'number_of_visited_cities': modification__visited(number_of_visited_cities),
            'number_of_visited_cities_previous_year': modification__visited(
                number_of_total_visited_cities_previous_year
            ),
            'number_of_visited_cities_current_year': modification__visited(
                number_of_total_visited_cities_current_year
            ),
            'number_of_visited_regions': modification__visited(num_visited_regions),
        },
    }

    return context
