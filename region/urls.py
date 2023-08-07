from django.urls import path
from . import views

urlpatterns = [
    path('all/list', views.RegionList.as_view(list_or_map='list'), name='region-all-list'),
    path('all/map', views.RegionList.as_view(list_or_map='map'), name='region-all-map'),
    path('<int:pk>', views.CitiesByRegionList.as_view(), name='region-selected'),
]
