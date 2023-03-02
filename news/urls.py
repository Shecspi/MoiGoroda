from django.urls import path
from . import views

urlpatterns = [
    path('', views.News_List.as_view(), name='news-list'),
]
