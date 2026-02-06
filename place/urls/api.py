"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path

from place.api import (
    CreatePlace,
    CreatePlaceCollection,
    DeletePlace,
    GetPlaceCollections,
    GetPlaces,
    GetCategory,
    UpdatePlace,
)

urlpatterns = [
    path('', GetPlaces.as_view(), name='get_places'),
    path('create/', CreatePlace.as_view(), name='create_place'),
    path('delete/<int:pk>', DeletePlace.as_view(), name='delete_place'),
    path('update/<int:pk>', UpdatePlace.as_view(), name='update_place'),
    path('category/', GetCategory.as_view(), name='category_of_place'),
    path('collections/', GetPlaceCollections.as_view(), name='get_place_collections'),
    path(
        'collections/create/',
        CreatePlaceCollection.as_view(),
        name='create_place_collection',
    ),
]
