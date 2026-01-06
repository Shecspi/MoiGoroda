from django.urls import path

import city.api as api

urlpatterns = [
    path('visited', api.GetVisitedCities.as_view(), name='api__get_visited_cities'),
    path(
        'visited/subscriptions',
        api.GetVisitedCitiesFromSubscriptions.as_view(),
        name='api__get_visited_cities_from_subscriptions',
    ),
    path('not_visited', api.GetNotVisitedCities.as_view(), name='api__get_not_visited_cities'),
    path('visited/add', api.AddVisitedCity.as_view(), name='api__add_visited_city'),
    path('list_by_region', api.city_list_by_region, name='api__city_list_by_region'),
    path('list_by_regions', api.city_list_by_regions, name='api__city_list_by_regions'),
    path('list_by_ids', api.city_list_by_ids, name='api__city_list_by_ids'),
    path(
        'list_by_country',
        api.city_list_by_country,
        name='api__city_list_by_country',
    ),
    path('search', api.city_search, name='city_search'),
    path('country/list_by_cities', api.country_list_by_cities, name='api__country_list_by_cities'),
    path(
        'list/default_settings',
        api.save_city_list_default_settings,
        name='api__save_city_list_default_settings',
    ),
    path(
        'list/default_settings/delete',
        api.delete_city_list_default_settings,
        name='api__delete_city_list_default_settings',
    ),
    path('visit_years', api.get_visit_years, name='api__get_visit_years'),
]
