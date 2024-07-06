from django.urls import path

import city.api
from city.views import (
    GetVisitedCitiesFromSubscriptions_API,
    GetVisitedCities_API,
    GetNotVisitedCities_API,
)

urlpatterns = [
    # /api/city/visiited
    path('visited', GetVisitedCities_API.as_view(), name='api__get_visited_cities'),
    # /api/city/visited/2023
    path(
        'visited/<int:year>',
        city.api.get_visited_cities_by_year,
        name='api__get_visited_cities_by_year',
    ),
    # /api/city/subscriptions
    path(
        'visited/subscriptions',
        GetVisitedCitiesFromSubscriptions_API.as_view(),
        name='api__get_visited_cities_from_subscriptions',
    ),
    # /api/city/not_visited
    path('not_visited', GetNotVisitedCities_API.as_view(), name='api__get_not_visited_cities'),
]
