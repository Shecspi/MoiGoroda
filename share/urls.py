from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/', views.Share.as_view(), name='share'),
    path('<int:pk>/<str:requested_page>/', views.Share.as_view(), name='share'),
]
