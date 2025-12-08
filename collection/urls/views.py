"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from collection import views

urlpatterns = [
    path('', views.CollectionList.as_view(), name='collection-list'),
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
    path(
        '<int:pk>/map',
        views.CollectionSelected_List.as_view(list_or_map='map'),
        name='collection-detail-map',
    ),
]
