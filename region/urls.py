from django.urls import path
from . import views

urlpatterns = [
    path('all', views.Region_List.as_view(), name='region-all'),
    path('<int:pk>', views.CitiesByRegion_List.as_view(), name='region-selected'),
]
