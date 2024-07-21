from django.urls import path

from city.api import (
    GetVisitedCitiesFromSubscriptions,
    GetVisitedCities,
    GetNotVisitedCities,
)

urlpatterns = [
    # /api/city/visiited
    path('visited', GetVisitedCities.as_view(), name='api__get_visited_cities'),
    # /api/city/subscriptions
    path(
        'visited/subscriptions',
        GetVisitedCitiesFromSubscriptions.as_view(),
        name='api__get_visited_cities_from_subscriptions',
    ),
    # /api/city/not_visited
    path('not_visited', GetNotVisitedCities.as_view(), name='api__get_not_visited_cities'),
]
