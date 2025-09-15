from django.urls import path

from region.api import region_list_by_country, search_region

urlpatterns = [
    path('list', region_list_by_country, name='region-list-by-country'),
    path('search', search_region, name='search-region'),
]
