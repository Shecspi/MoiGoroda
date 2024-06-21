"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from . import views

urlpatterns = [
    # Списки с городами
    path('all/list', views.VisitedCity_List.as_view(list_or_map='list'), name='city-all-list'),
    path('all/map', views.VisitedCity_List.as_view(list_or_map='map'), name='city-all-map'),
    path('<int:pk>', views.VisitedCity_Detail.as_view(), name='city-selected'),
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
    path('api/get_users_cities', views.get_users_cities, name='get_users_cities'),
]
