"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from collection.api import collection_search, favorite_collection_toggle

urlpatterns = [
    path('search', collection_search, name='collection_search'),
    path('favorite/<int:collection_id>', favorite_collection_toggle, name='favorite_collection_toggle'),
]
