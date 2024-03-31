"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from . import views

urlpatterns = [
    path('all/list', views.RegionList.as_view(list_or_map='list'), name='region-all-list'),
    path('all/map', views.RegionList.as_view(list_or_map='map'), name='region-all-map'),
    path(
        '<int:pk>/list',
        views.CitiesByRegionList.as_view(list_or_map='list'),
        name='region-selected-list',
    ),
    path(
        '<int:pk>/map',
        views.CitiesByRegionList.as_view(list_or_map='map'),
        name='region-selected-map',
    ),
]
