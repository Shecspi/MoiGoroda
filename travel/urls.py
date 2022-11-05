from django.urls import path
from . import views

urlpatterns = [
    # Списки с городами
    path('city/all/', views.VisitedCity_List.as_view(), name='city-all'),
    path('city/<int:pk>', views.VisitedCity_Detail.as_view(), name='city-selected'),

    # Операции с городами
    path('city/create/', views.VisitedCity_Create.as_view(), name='city-create'),
    path('city/delete/<int:pk>', views.VisitedCity_Delete.as_view(), name='city-delete'),
    path('city/update/<int:pk>', views.VisitedCity_Update.as_view(), name='city-update'),

    # Списки регионов
    path('region/all', views.Region_List.as_view(), name='region-all'),
    path('region/<int:pk>', views.VisitedCity_List.as_view(), name='region-selected'),

    # API
    path('api/get_cities_based_on_region/', views.get_cities_based_on_region, name='get_cities_based_on_region'),
]
