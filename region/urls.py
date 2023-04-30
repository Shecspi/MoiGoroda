from django.urls import path
from . import views

urlpatterns = [
    path('all', views.RegionList.as_view(), name='region-all'),
    path('<int:pk>', views.CitiesByRegionList.as_view(), name='region-selected'),
]
