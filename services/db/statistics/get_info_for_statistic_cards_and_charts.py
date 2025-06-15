import datetime

from region.services.db import (
    get_all_region_with_visited_cities,
    get_number_of_regions,
    get_number_of_visited_regions,
    get_number_of_finished_regions,
)
from services.word_modifications.city import *
from services.word_modifications.region import *
from services.word_modifications.visited import *
from city.services.db import (
    get_number_of_new_visited_cities,
    get_number_of_total_visited_cities_by_year,
    get_number_of_new_visited_cities_by_year,
    get_number_of_total_visited_cities_in_several_month,
    get_number_of_total_visited_cities_in_several_years,
    get_number_of_new_visited_cities_in_several_years,
    get_number_of_new_visited_cities_in_several_month,
    get_number_of_visited_cities,
    get_last_10_new_visited_cities,
)
from country.repository import (
    get_countries_with_visited_city,
    get_countries_with_visited_city_in_year,
    get_countries_with_new_visited_city_in_year,
    get_list_of_countries_with_visited_regions,
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
    number_of_new_visited_cities = get_number_of_new_visited_cities(user_id)
    # number_of_not_visited_cities = get_number_of_not_visited_cities(user_id)
    #
    number_of_visited_cities_current_year = get_number_of_total_visited_cities_by_year(
        user_id, current_year
    )
    number_of_new_visited_cities_current_year = get_number_of_new_visited_cities_by_year(
        user_id, current_year
    )
    number_of_visited_cities_previous_year = get_number_of_total_visited_cities_by_year(
        user_id, current_year - 1
    )
    number_of_new_visited_cities_previous_year = get_number_of_new_visited_cities_by_year(
        user_id, current_year - 1
    )
    list_of_all_countries_with_visited_cities = get_countries_with_visited_city(user_id)
    # Страны с посещёнными городами (включая повторные посещения) в текущем году
    list_of_countries_with_visited_cities_current_year = get_countries_with_visited_city_in_year(
        user_id, current_year
    )
    # Страны с новыми посещёнными городами в текущем году
    list_of_countries_with_new_visited_cities_current_year = (
        get_countries_with_new_visited_city_in_year(user_id, current_year)
    )
    # Страны с посещёнными городами (включая повторные посещения) в прошлом году
    list_of_countries_with_visited_cities_previous_year = get_countries_with_visited_city_in_year(
        user_id, current_year - 1
    )
    # Страны с новыми посещёнными городами в прошлом году
    list_of_countries_with_new_visited_cities_previous_year = (
        get_countries_with_new_visited_city_in_year(user_id, current_year - 1)
    )
    # ratio_cities_this_year = calculate_ratio(
    #     number_of_total_visited_cities_current_year, number_of_total_visited_cities_previous_year
    # )
    # ratio_cities_prev_year = 100 - ratio_cities_this_year
    #
    number_of_visited_cities_in_several_years = get_number_of_total_visited_cities_in_several_years(
        user_id
    )
    number_of_new_visited_cities_in_several_years = (
        get_number_of_new_visited_cities_in_several_years(user_id)
    )
    number_of_visited_cities_in_several_month = get_number_of_total_visited_cities_in_several_month(
        user_id
    )
    number_of_new_visited_cities_in_several_month = (
        get_number_of_new_visited_cities_in_several_month(user_id)
    )
    #
    context['cities'] = {
        'number_of_visited_cities': number_of_visited_cities,
        'number_of_new_visited_cities': number_of_new_visited_cities,
        'last_10_visited_cities': get_last_10_new_visited_cities(user_id),
        'number_of_visited_cities_current_year': number_of_visited_cities_current_year,
        'number_of_new_visited_cities_current_year': number_of_new_visited_cities_current_year,
        'number_of_visited_cities_previous_year': number_of_visited_cities_previous_year,
        'number_of_new_visited_cities_previous_year': number_of_new_visited_cities_previous_year,
        'list_of_all_countries_with_visited_cities': list_of_all_countries_with_visited_cities,
        'list_of_countries_with_visited_cities_current_year': list_of_countries_with_visited_cities_current_year,
        'list_of_countries_with_new_visited_cities_current_year': list_of_countries_with_new_visited_cities_current_year,
        'list_of_countries_with_visited_cities_previous_year': list_of_countries_with_visited_cities_previous_year,
        'list_of_countries_with_new_visited_cities_previous_year': list_of_countries_with_new_visited_cities_previous_year,
        #     'ratio_cities_this_year': ratio_cities_this_year,
        #     'ratio_cities_prev_year': ratio_cities_prev_year,
        'number_of_visited_cities_in_several_years': number_of_visited_cities_in_several_years,
        'number_of_new_visited_cities_in_several_years': number_of_new_visited_cities_in_several_years,
        'number_of_visited_cities_in_several_month': number_of_visited_cities_in_several_month,
        'number_of_new_visited_cities_in_several_month': number_of_new_visited_cities_in_several_month,
    }
    #
    # ##################################
    # # --- Статистика по регионам --- #
    # ##################################
    country_id = 171  # Пока что показываем только российские регионы
    regions = get_all_region_with_visited_cities(user_id)
    number_of_regions = get_number_of_regions(country_id)
    number_of_visited_regions = get_number_of_visited_regions(user_id, country_id)
    number_of_not_visited_regions = number_of_regions - number_of_visited_regions
    number_of_finished_regions = get_number_of_finished_regions(user_id, country_id)
    list_of_countries_with_visited_regions = get_list_of_countries_with_visited_regions(user_id)
    list_of_countries_with_visited_regions_current_year = (
        get_list_of_countries_with_visited_regions(user_id, current_year)
    )
    list_of_countries_with_visited_regions_previous_year = (
        get_list_of_countries_with_visited_regions(user_id, current_year - 1)
    )
    list_of_countries_with_all_visited_regions = [
        country
        for country in list_of_countries_with_visited_regions
        if country.number_of_regions > 0
        and country.number_of_regions == country.number_of_visited_regions
    ]

    context['regions'] = {
        'most_visited_regions': regions[:10],
        'number_of_regions': number_of_regions,
        'number_of_visited_regions': number_of_visited_regions,
        'number_of_not_visited_regions': number_of_not_visited_regions,
        'number_of_finished_regions': number_of_finished_regions,
        'list_of_countries_with_visited_regions': list_of_countries_with_visited_regions,
        'list_of_countries_with_visited_regions_current_year': list_of_countries_with_visited_regions_current_year,
        'list_of_countries_with_visited_regions_previous_year': list_of_countries_with_visited_regions_previous_year,
        'list_of_countries_with_all_visited_regions': list_of_countries_with_all_visited_regions,
    }
    #
    # #############################################
    # # --- Статистика по федеральным округам --- #
    # #############################################
    # areas = get_visited_areas(user_id)
    # number_all_areas = get_number_all_areas()
    # number_visited_areas = get_number_visited_areas(user_id)
    #
    # context['areas'] = {
    #     'list_of_areas': areas,
    #     'number_all_areas': number_all_areas,
    #     'number_visited_areas': number_visited_areas,
    #     'number_not_visited_areas': number_all_areas - number_visited_areas,
    # }
    #
    # ####################
    # # Изменённые слова #
    # ####################
    # context['word_modifications'] = {
    #     'city': {
    #         'number_of_visited_cities': modification__city(number_of_visited_cities),
    #         'number_of_not_visited_cities': modification__city(number_of_not_visited_cities),
    #         'number_of_total_visited_cities_current_year': modification__city(
    #             number_of_total_visited_cities_current_year
    #         ),
    #         'number_of_new_visited_cities_current_year': modification__city(
    #             number_of_new_visited_cities_current_year
    #         ),
    #         'number_of_total_visited_cities_previous_year': modification__city(
    #             number_of_total_visited_cities_previous_year
    #         ),
    #         'number_of_new_visited_cities_previous_year': modification__city(
    #             number_of_new_visited_cities_previous_year
    #         ),
    #     },
    #     'region': {
    #         'number_of_visited_regions': modification__region__accusative_case(num_visited_regions),
    #         'number_of_not_visited_regions': modification__region__accusative_case(
    #             number_of_regions - num_visited_regions
    #         ),
    #         'number_of_finished_regions': modification__region__prepositional_case(
    #             num_finished_regions
    #         ),
    #     },
    #     'visited': {
    #         'number_of_visited_cities': modification__visited(number_of_visited_cities),
    #         'number_of_visited_cities_previous_year': modification__visited(
    #             number_of_total_visited_cities_previous_year
    #         ),
    #         'number_of_visited_cities_current_year': modification__visited(
    #             number_of_total_visited_cities_current_year
    #         ),
    #         'number_of_visited_regions': modification__visited(num_visited_regions),
    #     },
    # }

    return context
