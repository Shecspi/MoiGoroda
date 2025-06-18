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
    path(
        'list_by_country',
        api.city_list_by_country,
        name='api__city_list_by_country',
    ),
]
