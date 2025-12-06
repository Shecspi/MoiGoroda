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
        'personal/create',
        views.PersonalCollectionCreate.as_view(),
        name='collection-personal-create',
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
