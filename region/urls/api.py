from django.urls import path

from region.api import region_list_by_country

urlpatterns = [
    path('list', region_list_by_country, name='region-list-by-country'),
]
