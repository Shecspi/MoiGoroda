# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from django.urls import path
from dmr.routing import path as dmr_path
from region import views
from region.fragment_api import CitiesByRegionListFragmentController, RegionListFragmentController

urlpatterns = [
    path('all/list', views.RegionList.as_view(list_or_map='list'), name='region-all-list'),
    dmr_path(
        'all/list/fragment',
        RegionListFragmentController.as_view(),
        name='region-all-list-fragment',
    ),
    path('all/map', views.RegionList.as_view(list_or_map='map'), name='region-all-map'),
    path(
        '<int:pk>/list',
        views.CitiesByRegionList.as_view(list_or_map='list'),
        name='region-selected-list',
    ),
    dmr_path(
        '<int:pk>/list/fragment',
        CitiesByRegionListFragmentController.as_view(),
        name='region-selected-list-fragment',
    ),
    path(
        '<int:pk>/map',
        views.CitiesByRegionList.as_view(list_or_map='map'),
        name='region-selected-map',
    ),
    path(
        '<int:pk>/share/',
        views.RegionShareView.as_view(),
        name='region-share',
    ),
    path('embedded/<str:quality>/RU/<str:iso3166>', views.embedded_map, name='region-embedded-map'),
]
