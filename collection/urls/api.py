"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from collection.api import collection_search

urlpatterns = [
    path('search', collection_search, name='collection_search'),
]
