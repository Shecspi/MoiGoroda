"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from city import views
from city.repository.city_repository import CityRepository
from city.repository.visited_city_repository import VisitedCityRepository
from city.services.visited_city_service import VisitedCityService

urlpatterns = [
    # Списки с городами
    path('all/list', views.VisitedCity_List.as_view(), name='city-all-list'),
    path('all/map', views.VisitedCity_Map.as_view(), name='city-all-map'),
    path(
        '<int:pk>',
        views.VisitedCityDetail.as_view(
            service_factory=lambda request: VisitedCityService(
                CityRepository(),
                VisitedCityRepository(),
                request,
            )
        ),
        name='city-selected',
    ),
    # Операции с городами
    path('create/', views.VisitedCity_Create.as_view(), name='city-create'),
    path('delete/<int:pk>', views.VisitedCity_Delete.as_view(), name='city-delete'),
    path('update/<int:pk>', views.VisitedCity_Update.as_view(), name='city-update'),
    # API
    path(
        'api/get_cities_based_on_region/',
        views.get_cities_based_on_region,
        name='get_cities_based_on_region',
    ),
    path(
        'districts/<int:city_id>/map',
        views.CityDistrictMapView.as_view(),
        name='city-districts-map',
    ),
]
