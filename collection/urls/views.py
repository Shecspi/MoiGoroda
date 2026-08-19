# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from django.urls import path
from dmr.routing import path as dmr_path
from collection import views
from collection.fragment_api import (
    CollectionListFragmentController,
    CollectionSelectedListFragmentController,
)

urlpatterns = [
    path('', views.CollectionList.as_view(), name='collection-list'),
    dmr_path(
        'fragment',
        CollectionListFragmentController.as_view(),
        name='collection-list-fragment',
    ),
    path(
        'personal',
        views.PersonalCollectionListView.as_view(),
        name='collection-personal-list-view',
    ),
    path(
        'personal/public',
        views.PublicPersonalCollectionListView.as_view(),
        name='collection-personal-public-list-view',
    ),
    path(
        'personal/create',
        views.PersonalCollectionCreate.as_view(),
        name='collection-personal-create',
    ),
    path(
        'personal/<uuid:pk>/edit',
        views.PersonalCollectionEdit.as_view(),
        name='collection-personal-edit',
    ),
    path(
        'personal/<uuid:pk>/list',
        views.PersonalCollectionCityListView.as_view(),
        name='collection-personal-list',
    ),
    path(
        'personal/<uuid:pk>/map',
        views.PersonalCollectionMap.as_view(),
        name='collection-personal-map',
    ),
    path(
        '<int:pk>/list',
        views.CollectionSelected_List.as_view(list_or_map='list'),
        name='collection-detail-list',
    ),
    dmr_path(
        '<int:pk>/list/fragment',
        CollectionSelectedListFragmentController.as_view(),
        name='collection-detail-list-fragment',
    ),
    path(
        '<int:pk>/map',
        views.CollectionSelected_List.as_view(list_or_map='map'),
        name='collection-detail-map',
    ),
]
