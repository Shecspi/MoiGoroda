"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.urls import path
from collection.api import search_region

urlpatterns = [
    path('search', search_region, name='search-region'),
]
