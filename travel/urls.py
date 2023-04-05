from django.urls import path
from . import views

urlpatterns = [
    # Списки с городами
    path('all/', views.VisitedCity_List.as_view(), name='city-all'),
    path('<int:pk>', views.VisitedCity_Detail.as_view(), name='city-selected'),

    # Операции с городами
    path('create/', views.VisitedCity_Create.as_view(), name='city-create'),
    path('delete/<int:pk>', views.VisitedCity_Delete.as_view(), name='city-delete'),
    path('update/<int:pk>', views.VisitedCity_Update.as_view(), name='city-update'),

    # API
    path('api/get_cities_based_on_region/', views.get_cities_based_on_region, name='get_cities_based_on_region'),
]
