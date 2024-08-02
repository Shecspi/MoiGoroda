from django.urls import path

import city.api as api

urlpatterns = [
    # /api/city/visiited
    path('visited', api.GetVisitedCities.as_view(), name='api__get_visited_cities'),
    # /api/city/subscriptions
    path(
        'visited/subscriptions',
        api.GetVisitedCitiesFromSubscriptions.as_view(),
        name='api__get_visited_cities_from_subscriptions',
    ),
    # /api/city/not_visited
    path('not_visited', api.GetNotVisitedCities.as_view(), name='api__get_not_visited_cities'),
    path('visited/add', api.AddVisitedCity.as_view(), name='api_add_visited_city'),
]
