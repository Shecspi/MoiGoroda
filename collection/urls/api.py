"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from collection.api import (
    collection_search,
    favorite_collection_toggle,
    personal_collection_create,
    personal_collection_update_public_status,
)

urlpatterns = [
    path('search', collection_search, name='collection_search'),
    path(
        'favorite/<int:collection_id>',
        favorite_collection_toggle,
        name='favorite_collection_toggle',
    ),
    path(
        'personal/create',
        personal_collection_create,
        name='api__personal_collection_create',
    ),
    path(
        'personal/<str:collection_id>/update-public-status',
        personal_collection_update_public_status,
        name='api__personal_collection_update_public_status',
    ),
]
