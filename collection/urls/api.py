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
    personal_collection_copy,
    personal_collection_create,
    personal_collection_delete,
    personal_collection_update,
    personal_collection_update_public_status,
    public_collections_statistics,
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
        'personal/<str:collection_id>/update',
        personal_collection_update,
        name='api__personal_collection_update',
    ),
    path(
        'personal/<str:collection_id>/update-public-status',
        personal_collection_update_public_status,
        name='api__personal_collection_update_public_status',
    ),
    path(
        'personal/<str:collection_id>/delete',
        personal_collection_delete,
        name='api__personal_collection_delete',
    ),
    path(
        'personal/<str:collection_id>/copy',
        personal_collection_copy,
        name='api__personal_collection_copy',
    ),
    path(
        'personal/public/statistics',
        public_collections_statistics,
        name='api__public_collections_statistics',
    ),
]
